from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024 * 1024  # 60GBまでOK

UPLOAD_FOLDER = Path("/data/rendering")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@app.route("/")
def hello():
    return "Hello from Flask in Docker!6"


@app.route("/upload_test")
def upload_test():
    html_file_path = Path(__file__).parent / 'upload_test.html'
    try:
        html_content = html_file_path.read_text(encoding='utf-8')
        return html_content
    except FileNotFoundError:
        return "upload_test.html ファイルが見つかりません。", 404


@app.route('/upload', methods=['POST'])
def upload():
    filename = request.headers.get('X-Filename', 'data.zip')
    filepath = UPLOAD_FOLDER / filename

    try:
        with filepath.open('wb') as f:
            chunk_size = 10 * 1024 * 1024  # 10MBずつ
            while True:
                chunk = request.stream.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
    except PermissionError:
        return jsonify({"status": "error", "message": "Permission denied: cannot write to upload folder"}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error saving file: {str(e)}"}), 500

    return jsonify({"status": "success", "message": "Upload complete", "filename": filename}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
