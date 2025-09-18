import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dotenv import load_dotenv
import os
import threading
import time
import requests
from mltpy.editor import MLTEditor
from mltpy.packager import MLTDataPackager

BG_COLOR = "#323232"   # 背景（濃いグレー）
FG_COLOR = "#E2E2E2"   # テキスト（白）
BTN_COLOR = "#175C76"  # アクセント（青系）

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shotcut MLT Toolbox")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("500x500")

        # ===== Processing Options Area =====
        frame_choices = tk.LabelFrame(root, text="Processing Options / 処理オプション", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_choices.pack(fill="x", padx=20, pady=10)

        # ラジオボタン用の共有変数
        self.wrap_choice_var = tk.StringVar(value="wrap_subtitles")

        # ラジオボタンの作成
        tk.Radiobutton(frame_choices, text="Wrap Subtitles / 字幕を折り返す", variable=self.wrap_choice_var, value="wrap_subtitles", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR, command=self.on_choice_change).pack(anchor="w")
        tk.Radiobutton(frame_choices, text="Wrap Simple Text / シンプルテキストを折り返す", variable=self.wrap_choice_var, value="wrap_dynamictext", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR, command=self.on_choice_change).pack(anchor="w")
        tk.Radiobutton(frame_choices, text="Cloud Rendering / クラウドレンダリング (Test version)", variable=self.wrap_choice_var, value="cloud_rendering", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR, command=self.on_choice_change).pack(anchor="w")

        # --- Details Options LabelFrame ---
        # Create a single LabelFrame to hold all the detail-related widgets.
        self.frame_details = tk.LabelFrame(root, text="Details Options / 詳細オプション", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        self.frame_details.pack(fill="x", padx=20, pady=10)

        # --- Force Wrap Checkbutton ---
        # This widget will be on the first line inside the frame.
        self.force_wrap_var = tk.BooleanVar()
        tk.Checkbutton(self.frame_details, text="Force Wrap / 強制折り返し", variable=self.force_wrap_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        # --- Max Length Label and Entry (on a single line) ---
        # Create a new Frame to group the label and entry horizontally.
        input_frame = tk.Frame(self.frame_details, bg=BG_COLOR)
        input_frame.pack(anchor="w", pady=(5, 0)) # Add a little padding at the top

        # Place the Label on the left side of the input_frame.
        tk.Label(input_frame, text="Max Length / 最大長", fg=FG_COLOR, bg=BG_COLOR).pack(side="left", padx=(0, 10))

        # Place the Entry next to the Label.
        self.wrap_max_length_var = tk.IntVar(value=90)
        tk.Entry(input_frame, textvariable=self.wrap_max_length_var, width=10).pack(side="left")


        # ===== File Selection Area =====
        frame_file = tk.LabelFrame(root, text="File Selection / ファイル選択", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_file.pack(fill="x", padx=20, pady=10)

        self.input_path_var = tk.StringVar()
        tk.Entry(frame_file, textvariable=self.input_path_var, width=40).pack(side="left", padx=5)
        tk.Button(frame_file, text="Browse / 参照", bg=BTN_COLOR, fg=FG_COLOR, command=self.browse_file).pack(side="left")

        # ===== Execution Button =====
        tk.Button(root, text="Run / 実行", bg=BTN_COLOR, fg=FG_COLOR, width=20, height=2, command=self.run).pack(pady=20)

        # ===== Progress Display Area =====
        self.progress_frame = tk.Frame(root, bg=BG_COLOR)
        # 初期状態では非表示
        
        # 進捗状態ラベル
        self.status_label = tk.Label(self.progress_frame, text="状態: 未実行", fg=FG_COLOR, bg=BG_COLOR)
        self.status_label.pack(anchor="w")
        
        # 進捗バー
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # 進捗数値表示
        self.progress_text = tk.Label(self.progress_frame, text="", fg=FG_COLOR, bg=BG_COLOR)
        self.progress_text.pack(anchor="w", pady=(2, 0))
        
        # ダウンロードリンク
        self.download_link = tk.Label(self.progress_frame, text="", fg=FG_COLOR, bg=BG_COLOR, cursor="hand2")
        self.download_link.pack(anchor="w", pady=(5, 0))
        
        # クラウドレンダリング用の変数
        self.unique_id = None
        self.polling_thread = None
        self.is_polling = False

    def on_choice_change(self):
        """ラジオボタン選択時の詳細オプション表示/非表示切り替え"""
        choice = self.wrap_choice_var.get()
        if choice == "cloud_rendering":
            # Cloud Rendering選択時は詳細オプションを非表示、進捗フレームを表示
            self.frame_details.pack_forget()
            self.progress_frame.pack(fill="x", padx=20, pady=10)
        else:
            # その他の選択時は詳細オプションを表示、進捗フレームを非表示
            self.frame_details.pack(fill="x", padx=20, pady=10)
            self.progress_frame.pack_forget()

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MLT files", "*.mlt")])
        if file_path:
            self.input_path_var.set(file_path)

    def run(self):
        choice = self.wrap_choice_var.get()
        
        if choice == "cloud_rendering":
            self.run_cloud_rendering()
        else:
            self.run_local_processing()

    def run_local_processing(self):
        """ローカル処理（既存の機能）"""
        load_dotenv()
        if not os.getenv("GCLOUD_PROJECT_ID"):
            messagebox.showerror("エラー", "環境変数 GCLOUD_PROJECT_ID が設定されていません。\n.env ファイルを作成してください。")
            return

        try:
            editor = MLTEditor(self.input_path_var.get())

            choice = self.wrap_choice_var.get()
            if choice == "wrap_subtitles":
                editor.wrap_srt_lines(max_length=self.wrap_max_length_var.get(), force_wrap=self.force_wrap_var.get())
            elif choice == "wrap_dynamictext":
                editor.wrap_dynamictext_lines(max_length=self.wrap_max_length_var.get(), force_wrap=self.force_wrap_var.get())

            editor.save()
            messagebox.showinfo("完了", "処理が完了しました！")

        except Exception as e:
            messagebox.showerror("エラー", str(e))

    def run_cloud_rendering(self):
        """クラウドレンダリング処理"""
        if not self.input_path_var.get():
            messagebox.showerror("エラー", "ファイルを選択してください。")
            return

        # 進捗表示をリセット
        self.reset_progress()
        
        # バックグラウンドで実行
        thread = threading.Thread(target=self._cloud_rendering_worker)
        thread.daemon = True
        thread.start()

    def _cloud_rendering_worker(self):
        """クラウドレンダリングのワーカースレッド"""
        try:
            # Status 状態: Uploading アップロード
            self.root.after(0, lambda: self.update_status("Status 状態: Uploading アップロード"))
            
            # packagerを使用してZIP作成とアップロード
            packager = MLTDataPackager(self.input_path_var.get())
            zip_path = packager.prepare_zip()  # data.zip を生成
            
            # アップロード進捗コールバックを設定
            def upload_progress_callback(progress, uploaded_bytes, total_bytes):
                self.root.after(0, lambda: self._update_upload_progress(progress, uploaded_bytes, total_bytes))
            
            status, text = packager.upload(progress_callback=upload_progress_callback)   # アップロード
            
            print(f"ZIP path: {zip_path}, Status: {status}, Response: {text}")
            
            if status == 200:
                # アップロード成功時、レスポンスからunique_idを取得
                try:
                    import json
                    response_data = json.loads(text)
                    self.unique_id = response_data.get('unique_id')
                    if self.unique_id:
                        # ポーリング開始（キュー待機状態も含む）
                        self.start_polling()
                    else:
                        self.root.after(0, lambda: messagebox.showerror("エラー", "アップロードレスポンスにunique_idが含まれていません"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("エラー", f"アップロードレスポンスの解析に失敗: {e}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("エラー", f"アップロードに失敗しました。ステータス: {status}, レスポンス: {text}"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("エラー", f"クラウドレンダリング処理中にエラーが発生しました: {e}"))

    def reset_progress(self):
        """進捗表示をリセット"""
        self.status_label.config(text="Status 状態: Not Running 未実行")
        self.progress_bar['value'] = 0
        self.progress_text.config(text="")
        self.download_link.config(text="")
        self.unique_id = None
        self.is_polling = False

    def update_status(self, status):
        """ステータスを更新"""
        self.status_label.config(text=status)

    def start_polling(self):
        """ステータスポーリングを開始"""
        if self.is_polling:
            return
        
        self.is_polling = True
        self.polling_thread = threading.Thread(target=self._poll_status)
        self.polling_thread.daemon = True
        self.polling_thread.start()

    def _poll_status(self):
        """ステータスをポーリング"""
        while self.is_polling and self.unique_id:
            try:
                url = f"http://163.58.36.32:5000/status/{self.unique_id}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', '')
                    progress = data.get('progress', 0)  # パーセント値
                    current = data.get('current', 0)    # 達成したクリップ数
                    total = data.get('total', 0)        # 総クリップ数
                    
                    # デバッグ用ログ出力（詳細版）
                    print(f"Status response: {data}")
                    print(f"Parsed - Status: '{status}', Progress: {progress}, Current: {current}, Total: {total}")
                    
                    # progressが100%の場合は完了として扱う
                    if progress >= 100:
                        status = 'completed'
                        print("Progress reached 100%, setting status to 'completed'")
                    
                    # UIを更新
                    self.root.after(0, lambda s=status, p=progress, c=current, t=total: self._update_progress(s, p, c, t))
                    
                    if status == 'completed':
                        # 完了時はダウンロードリンクを表示
                        self.root.after(0, lambda: self._show_download_link())
                        self.is_polling = False
                        break
                    elif status == 'error':
                        self.root.after(0, lambda: messagebox.showerror("エラー", "レンダリング中にエラーが発生しました"))
                        self.is_polling = False
                        break
                    elif status in ['rendering', 'running', 'processing']:
                        # レンダリング中（複数のステータス名に対応）
                        print(f"Rendering status detected: {status}")
                        # ポーリングを継続
                    else:
                        # その他の状態
                        print(f"Unknown status: {status}, continuing polling...")
                        # ポーリングを継続
                        
            except Exception as e:
                print(f"ポーリングエラー: {e}")
                
            time.sleep(2)  # 2秒間隔でポーリング

    def _update_upload_progress(self, progress, uploaded_bytes, total_bytes):
        """アップロード進捗を更新"""
        # 進捗バーを更新
        self.progress_bar['value'] = progress
        
        # 数値表示を更新（GB単位で表示）
        uploaded_gb = uploaded_bytes / (1024**3)
        total_gb = total_bytes / (1024**3)
        self.progress_text.config(text=f"{progress:.0f}% ({uploaded_gb:.2f}GB / {total_gb:.2f}GB)")
    
    def _update_progress(self, status, progress, current, total):
        """進捗を更新"""
        # デバッグ用ログ出力
        print(f"Updating progress - Status: {status}, Progress: {progress}, Current: {current}, Total: {total}")
        
        if status in ['rendering', 'running', 'processing']:
            # レンダリング中（複数のステータス名に対応）
            self.status_label.config(text="Status 状態: Rendering レンダリング")
            # progressは既にパーセント値なので、そのまま使用
            self.progress_bar['value'] = progress
            if total > 0:
                self.progress_text.config(text=f"{progress:.0f}% ({current}/{total})")
            else:
                self.progress_text.config(text=f"{progress:.0f}%")
        elif status == 'completed':
            self.status_label.config(text="Status 状態: Completed 完了")
            self.progress_bar['value'] = 100
            self.progress_text.config(text="100% (完了)")
        else:
            # その他の状態（エラーなど）
            self.status_label.config(text=f"Status 状態: {status}")
            self.progress_bar['value'] = 0
            self.progress_text.config(text="")

    def _show_download_link(self):
        """ダウンロードリンクを表示"""
        if self.unique_id:
            download_url = f"http://163.58.36.32:5000/download/{self.unique_id}"
            self.download_link.config(text=f"Download ダウンロード: {download_url}")
            self.download_link.bind("<Button-1>", lambda e: self._open_download_link(download_url))

    def _open_download_link(self, url):
        """ダウンロードリンクを開く"""
        import webbrowser
        webbrowser.open(url)

def main():
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
