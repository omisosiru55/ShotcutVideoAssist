from flask import Flask, request, jsonify, send_file
from pathlib import Path
import threading
import subprocess
import zipfile
import secrets
import string
import re
import xml.etree.ElementTree as ET
from functools import wraps
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024 * 1024  # 60GBまでOK

UPLOAD_FOLDER = Path("/data/rendering")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# 進行状況を追跡する辞書
progress_dict = {}  # uid -> { 'current': 0, 'total': 1, 'status': 'running' }

# 許可するIP（必要に応じて拡張可）
ALLOWED_IPS = {"163.58.36.32"}

def get_client_ip() -> str:
    # リバースプロキシ配下を想定してX-Forwarded-Forを優先
    xff = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if xff:
        return xff
    return request.remote_addr or ""

def ip_restricted(view_func):
    @wraps(view_func)
    def _wrapped(*args, **kwargs):
        client_ip = get_client_ip()
        if client_ip not in ALLOWED_IPS:
            return jsonify({"status": "error", "message": "Forbidden from this IP"}), 403
        return view_func(*args, **kwargs)
    return _wrapped

def generate_unique_id():
    """16桁の大文字小文字数字のユニークIDを生成"""
    alphabet = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(16))

def get_mlt_duration(mlt_file):
    """MLTファイルから総フレーム数を取得。

    優先順:
      1) tractor@out のタイムコード × profileのfps
      2) root@out が数値ならそれをフレーム数として採用
      3) playlist の entry in/out から合計フレーム数を推定
    """
    def parse_timecode_to_seconds(tc: str) -> float:
        # 形式: HH:MM:SS.mmm または HH:MM:SS:FF の可能性もあるが、ここではミリ秒形式に対応
        try:
            hh, mm, ss_ms = tc.split(':')
            hh = int(hh)
            mm = int(mm)
            if '.' in ss_ms:
                ss, ms = ss_ms.split('.')
                ss = int(ss)
                ms = int(ms.ljust(3, '0')[:3])  # 桁不足は0埋め
                return hh * 3600 + mm * 60 + ss + ms / 1000.0
            else:
                ss = int(ss_ms)
                return hh * 3600 + mm * 60 + ss
        except Exception:
            return 0.0

    try:
        tree = ET.parse(mlt_file)
        root = tree.getroot()

        # fpsを profile から取得
        fps_num = 0
        fps_den = 1
        profile = root.find('profile')
        if profile is not None:
            try:
                fps_num = int(profile.get('frame_rate_num', '0'))
                fps_den = int(profile.get('frame_rate_den', '1'))
            except ValueError:
                fps_num, fps_den = 0, 1
        fps = (fps_num / fps_den) if fps_den != 0 else 0

        # 1) tractor の out (タイムコード) を優先
        tractor = root.find('tractor')
        if tractor is not None:
            tc_out = tractor.get('out')
            if tc_out:
                seconds = parse_timecode_to_seconds(tc_out)
                if fps > 0 and seconds > 0:
                    return max(1, int(round(seconds * fps)))

    except Exception as e:
        print(f"Error parsing MLT file: {e}")
        return 1

def render_with_progress(mlt_file, output_file, uid):
    """進行状況を追跡しながらレンダリングを実行"""
    # MLTファイルから総フレーム数を取得
    total_frames = get_mlt_duration(mlt_file)
    print(f"MLT duration: {total_frames} frames")
    
    progress_dict[uid] = {'current': 0, 'total': total_frames, 'status': 'running'}
    cmd = ["xvfb-run", "-a", "/usr/bin/melt", str(mlt_file), "-progress", "-consumer", f"avformat:{output_file}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    last_log_time = 0
    last_progress_time = 0
    
    for line in proc.stdout:
        line = line.strip()
        current_time = time.time()
        
        # デバッグログは1秒間隔で制限
        if current_time - last_log_time >= 1.0:
            print(f"Melt output: {line}")
            last_log_time = current_time
        
        # 複数のパターンでCurrent Positionを取得
        patterns = [
            r"Current Position:\s*(\d+)",
            r"Position:\s*(\d+)",
            r"Frame:\s*(\d+)",
            r"(\d+)\s*frames"
        ]
        
        for pattern in patterns:
            m = re.search(pattern, line)
            if m:
                current_pos = int(m.group(1))
                progress_dict[uid]['current'] = current_pos
                
                # 進捗ログも1秒間隔で制限
                if current_time - last_progress_time >= 1.0:
                    progress_pct = int(current_pos/total_frames*100) if total_frames > 0 else 0
                    print(f"Progress: {current_pos}/{total_frames} ({progress_pct}%)")
                    last_progress_time = current_time
                break

    proc.wait()
    progress_dict[uid]['current'] = progress_dict[uid]['total']
    progress_dict[uid]['status'] = 'completed'

def process_file(filepath: Path, unique_id: str):
    """バックグラウンドでZIP解凍とレンダリングを行う"""
    try:
        print(f"Processing file: {filepath} (ID: {unique_id})")
        
        # meltコマンドの存在確認
        melt_path = "/usr/bin/melt"
        if not Path(melt_path).exists():
            raise FileNotFoundError(f"Path check:melt command not found at {melt_path}")
        print(f"Path check successful")

        # 解凍用フォルダ（ユニークIDを使用）
        extract_dir = filepath.parent / unique_id
        extract_dir.mkdir(exist_ok=True)
        print(f"Extracting to: {extract_dir}")

        # zip解凍
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("ZIP extraction completed")

        # meltコマンドでレンダリング（進行状況付き）
        output_file = extract_dir / "output.mp4"
        mlt_file = extract_dir / "cloud_rendering.mlt"
        
        if not mlt_file.exists():
            raise FileNotFoundError(f"MLT file not found: {mlt_file}")
        
        print(f"Starting render with progress tracking (ID: {unique_id})")
        render_with_progress(mlt_file, output_file, unique_id)

        print(f"[OK] Render finished: {output_file}")

    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        progress_dict[unique_id] = {'current': 0, 'total': 1, 'status': 'error'}

@app.route("/")
def hello():
    return "Hello from Flask in Docker!6"


@app.route("/upload_test")
@ip_restricted
def upload_test():
    html_file_path = Path(__file__).parent / 'upload_test.html'
    try:
        html_content = html_file_path.read_text(encoding='utf-8')
        return html_content
    except FileNotFoundError:
        return "upload_test.html ファイルが見つかりません。", 404


@app.route("/progress_test")
@ip_restricted
def progress_test():
    html_file_path = Path(__file__).parent / 'progress_test.html'
    try:
        html_content = html_file_path.read_text(encoding='utf-8')
        return html_content
    except FileNotFoundError:
        return "progress_test.html ファイルが見つかりません。", 404


@app.route('/upload', methods=['POST'])
def upload():
    filename = request.headers.get('X-Filename', 'data.zip')
    
    # 16桁のユニークIDを生成
    unique_id = generate_unique_id()
    print(f"Generated unique ID: {unique_id}")
    
    # ユニークIDをファイル名として使用
    filepath = UPLOAD_FOLDER / f"{unique_id}.zip"
    
    try:
        print(f"Starting file upload to: {filepath}")
        with filepath.open('wb') as f:
            chunk_size = 10 * 1024 * 1024  # 10MBずつ
            while True:
                chunk = request.stream.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
        print(f"File upload completed: {filepath}")
    except PermissionError:
        return jsonify({"status": "error", "message": "Permission denied: cannot write to upload folder"}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error saving file: {str(e)}"}), 500

    # 非同期で解凍＆レンダリング開始
    threading.Thread(target=process_file, args=(filepath, unique_id), daemon=True).start()
    
    return jsonify({
        "status": "success", 
        "message": "Upload complete", 
        "original_filename": filename,
        "unique_id": unique_id,
        "download_url": f"/download/{unique_id}"
    }), 200


@app.route('/download/<unique_id>')
def download_file(unique_id):
    """レンダリング済みの動画ファイルをダウンロード"""
    try:
        # ファイルパスを構築（ユニークIDを使用）
        file_path = UPLOAD_FOLDER / unique_id / "output.mp4"
        
        if not file_path.exists():
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        # ファイルをダウンロードとして送信
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{unique_id}_output.mp4",
            mimetype="video/mp4"
        )
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Download failed: {str(e)}"}), 500


@app.route('/status/<unique_id>')
def status(unique_id):
    """レンダリングの進行状況を取得"""
    info = progress_dict.get(unique_id)
    if not info:
        return jsonify({"status": "error", "message": "ID not found"}), 404
    
    if info['total'] > 0:
        progress = int(info['current'] / info['total'] * 100)
    else:
        progress = 0
    
    return jsonify({
        "status": info['status'], 
        "progress": progress,
        "current": info['current'],
        "total": info['total']
    })


@app.route('/status')
def server_status():
    """サーバー全体の状況を取得"""
    try:
        # 実行中のジョブをカウント
        running_jobs = [uid for uid, info in progress_dict.items() if info['status'] == 'running']
        queue_count = len(running_jobs)
        
        # 現在実行中のジョブのID（最初のもの）
        current_job = running_jobs[0] if running_jobs else None
        
        # サーバーの状態を決定
        if queue_count == 0:
            server_status = "waiting"
        else:
            server_status = "processing"
        
        return jsonify({
            "status": server_status,
            "queue": queue_count,
            "current_job": current_job
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to get server status: {str(e)}"}), 500


@app.route('/list')
@ip_restricted
def list_files():
    """レンダリング済みファイルの一覧を取得"""
    try:
        files = []
        for item in UPLOAD_FOLDER.iterdir():
            if item.is_dir():
                output_file = item / "output.mp4"
                if output_file.exists():
                    files.append({
                        "unique_id": item.name,
                        "download_url": f"/download/{item.name}",
                        "size": output_file.stat().st_size,
                        "created": output_file.stat().st_ctime
                    })
        
        return jsonify({"status": "success", "files": files}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to list files: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
