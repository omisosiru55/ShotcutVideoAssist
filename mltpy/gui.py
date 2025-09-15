import tkinter as tk
from tkinter import filedialog, messagebox
from dotenv import load_dotenv
import os
from .editor import MLTEditor

BG_COLOR = "#323232"   # 背景（濃いグレー）
FG_COLOR = "#E2E2E2"   # テキスト（白）
BTN_COLOR = "#175C76"  # アクセント（青系）

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shotcut MLT Toolbox")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("500x500")

        # ===== ファイル選択エリア =====
        frame_file = tk.LabelFrame(root, text="ファイル選択", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_file.pack(fill="x", padx=20, pady=10)

        self.input_path_var = tk.StringVar()
        tk.Entry(frame_file, textvariable=self.input_path_var, width=40).pack(side="left", padx=5)
        tk.Button(frame_file, text="参照", bg=BTN_COLOR, fg=FG_COLOR, command=self.browse_file).pack(side="left")

        # ===== プレイリスト設定エリア =====
        frame_playlist = tk.LabelFrame(root, text="プレイリスト設定", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_playlist.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_playlist, text="プレイリストID", fg=FG_COLOR, bg=BG_COLOR).pack(side="left")
        self.playlist_id_var = tk.IntVar(value=0)
        tk.Entry(frame_playlist, textvariable=self.playlist_id_var, width=10).pack(side="left", padx=5)

        # ===== 最初の選択肢エリア =====
        frame_choices = tk.LabelFrame(root, text="処理オプション", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_choices.pack(fill="x", padx=20, pady=10)

        self.wrap_subtitles_var = tk.BooleanVar()
        tk.Checkbutton(frame_choices, text="字幕を折り返す", variable=self.wrap_subtitles_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        self.wrap_dynamictext_var = tk.BooleanVar()
        tk.Checkbutton(frame_choices, text="シンプルテキストを折り返す", variable=self.wrap_dynamictext_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        self.force_wrap_var = tk.BooleanVar()
        tk.Checkbutton(frame_choices, text="強制折り返し", variable=self.force_wrap_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        tk.Label(frame_choices, text="最大長", fg=FG_COLOR, bg=BG_COLOR).pack(anchor="w")
        self.wrap_max_length_var = tk.IntVar(value=90)
        tk.Entry(frame_choices, textvariable=self.wrap_max_length_var, width=10).pack(anchor="w", pady=5)

        # ===== データディレクトリ =====
        frame_data = tk.LabelFrame(root, text="データディレクトリ", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_data.pack(fill="x", padx=20, pady=10)

        self.data_dir_var = tk.StringVar(value=r"C:\\data")
        tk.Entry(frame_data, textvariable=self.data_dir_var, width=40).pack(side="left", padx=5)

        # ===== 実行ボタン =====
        tk.Button(root, text="実行", bg=BTN_COLOR, fg=FG_COLOR, width=20, height=2, command=self.run).pack(pady=20)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MLT files", "*.mlt")])
        if file_path:
            self.input_path_var.set(file_path)

    def run(self):
        load_dotenv()
        if not os.getenv("GCLOUD_PROJECT_ID"):
            messagebox.showerror("エラー", "環境変数 GCLOUD_PROJECT_ID が設定されていません。\n.env ファイルを作成してください。")
            return

        try:
            editor = MLTEditor(self.input_path_var.get())

            if self.wrap_subtitles_var.get():
                editor.wrap_srt_lines(max_length=self.wrap_max_length_var.get(), force_wrap=self.force_wrap_var.get())

            if self.wrap_dynamictext_var.get():
                editor.wrap_dynamictext_lines(max_length=self.wrap_max_length_var.get(), force_wrap=self.force_wrap_var.get())

            editor.save()
            messagebox.showinfo("完了", "処理が完了しました！")

        except Exception as e:
            messagebox.showerror("エラー", str(e))

def main():
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
