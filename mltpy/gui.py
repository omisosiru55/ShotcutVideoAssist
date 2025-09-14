import tkinter as tk
from tkinter import ttk

# Shotcutっぽいダークカラー例
BG_COLOR = "#323232"   # 背景（濃いグレー）
FG_COLOR = "#E2E2E2"   # テキスト（白）
BTN_COLOR = "#175C76"  # アクセント（青系）

def main():
    root = tk.Tk()
    root.title("Shotcut風 GUIサンプル")
    root.geometry("400x200")
    root.configure(bg=BG_COLOR)

    # ttkのスタイル適用
    style = ttk.Style()
    style.theme_use("default")

    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR)
    style.configure("TButton", background=BTN_COLOR, foreground=FG_COLOR, padding=6)
    style.map("TButton",
              background=[("active", "#1e88c7")])  # ボタン押下時の色

    # ラベル
    label = ttk.Label(root, text="Shotcut風カラーのGUIへようこそ")
    label.pack(pady=20)

    # ボタン
    button = ttk.Button(root, text="実行", command=lambda: print("ボタン押された"))
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
