import tkinter as tk
from tkinter import filedialog, messagebox
from dotenv import load_dotenv
import os
from mltpy.editor import MLTEditor

BG_COLOR = "#323232"   # 背景（濃いグレー）
FG_COLOR = "#E2E2E2"   # テキスト（白）
BTN_COLOR = "#175C76"  # アクセント（青系）

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shotcut MLT Toolbox")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("500x400")

        # ===== Processing Options Area =====
        frame_choices = tk.LabelFrame(root, text="Processing Options / 処理オプション", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_choices.pack(fill="x", padx=20, pady=10)

        # ラジオボタン用の共有変数
        self.wrap_choice_var = tk.StringVar(value="wrap_subtitles")

        # ラジオボタンの作成
        tk.Radiobutton(frame_choices, text="Wrap Subtitles / 字幕を折り返す", variable=self.wrap_choice_var, value="wrap_subtitles", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")
        tk.Radiobutton(frame_choices, text="Wrap Simple Text / シンプルテキストを折り返す", variable=self.wrap_choice_var, value="wrap_dynamictext", fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        # --- Details Options LabelFrame ---
        # Create a single LabelFrame to hold all the detail-related widgets.
        frame_details = tk.LabelFrame(root, text="Details Options / 詳細オプション", padx=10, pady=10, bg=BG_COLOR, fg=FG_COLOR)
        frame_details.pack(fill="x", padx=20, pady=10)

        # --- Force Wrap Checkbutton ---
        # This widget will be on the first line inside the frame.
        self.force_wrap_var = tk.BooleanVar()
        tk.Checkbutton(frame_details, text="Force Wrap / 強制折り返し", variable=self.force_wrap_var, fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).pack(anchor="w")

        # --- Max Length Label and Entry (on a single line) ---
        # Create a new Frame to group the label and entry horizontally.
        input_frame = tk.Frame(frame_details, bg=BG_COLOR)
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

            choice = self.wrap_choice_var.get()
            if choice == "wrap_subtitles":
                editor.wrap_srt_lines(max_length=self.wrap_max_length_var.get(), force_wrap=self.force_wrap_var.get())
            elif choice == "wrap_dynamictext":
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
