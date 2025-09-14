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
        self.root.title("MLT Editor GUI")
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

        # ===== オプション設定エリア =====
        frame_options = tk.LabelFrame(root, text="オプション", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_options.pack(fill="x", padx=20, pady=10)

        self.wrap_subtitles_var = tk.BooleanVar()
        tk.Checkbutton(frame_options, text="字幕を折り返す", variable=self.wrap_subtitles_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        self.wrap_dynamictext_var = tk.BooleanVar()
        tk.Checkbutton(frame_options, text="dynamictextを折り返す", variable=self.wrap_dynamictext_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        self.force_wrap_var = tk.BooleanVar()
        tk.Checkbutton(frame_options, text="強制折り返し", variable=self.force_wrap_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        tk.Label(frame_options, text="最大長", fg=FG_COLOR, bg=BG_COLOR).pack(anchor="w")
        self.wrap_max_length_var = tk.IntVar(value=90)
        tk.Entry(frame_options, textvariable=self.wrap_max_length_var, width=10).pack(anchor="w", pady=5)

        # ===== データディレクトリ =====
        frame_data = tk.LabelFrame(root, text="データディレクトリ", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_data.pack(fill="x", padx=20, pady=10)

        self.data_dir_var = tk.StringVar(value=r"C:\\data")
        tk.Entry(frame_data, textvariable=self.data_dir_var, width=40).pack(side="left", padx=5)

        # ===== 翻訳設定エリア =====
        frame_translate = tk.LabelFrame(root, text="翻訳設定", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_translate.pack(fill="x", padx=20, pady=10)

        self.translate_dynamictext_var = tk.BooleanVar()
        tk.Checkbutton(frame_translate, text="dynamictextを翻訳", variable=self.translate_dynamictext_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        tk.Label(frame_translate, text="翻訳元", fg=FG_COLOR, bg=BG_COLOR).pack(anchor="w")
        self.translate_from_var = tk.StringVar(value="en")
        tk.Entry(frame_translate, textvariable=self.translate_from_var, width=10).pack(anchor="w", pady=5)

        tk.Label(frame_translate, text="翻訳先", fg=FG_COLOR, bg=BG_COLOR).pack(anchor="w")
        self.translate_to_var = tk.StringVar(value="ja")
        tk.Entry(frame_translate, textvariable=self.translate_to_var, width=10).pack(anchor="w", pady=5)

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

            if self.translate_dynamictext_var.get():
                editor.translate_dynamictext(from_lang=self.translate_from_var.get(), to_lang=self.translate_to_var.get())

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
