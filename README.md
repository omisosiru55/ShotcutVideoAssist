# ShotcutVideoAssist v1.0.0

## Overview / 概要
**ShotcutVideoAssist** is a tool to batch-add subtitles to an existing MLT file.  
It automatically adds subtitles from a CSV file as sequential clips in the specified playlist.

**ShotcutVideoAssist** は、既存の MLT ファイルに字幕を一括追加するためのツールです。  
CSV ファイルから字幕を読み込み、指定したプレイリストに連続クリップとして自動追加します。

- Input / 入力: Existing MLT file + CSV file (1 column, 1 row = 1 subtitle / 1行 = 1字幕)  
- Output / 出力: `{original_filename}_subtitled.mlt`  
- Behavior / 動作: 1 subtitle = 1 clip (2 seconds / 2秒)  

---

## Installation / インストール
1. Download the v1.0.0 release from GitHub  
2. Extract to any folder  
3. Requires Python 3.x (tkinter included)  
#
1. GitHub から v1.0.0 リリースをダウンロード  
2. 適当なフォルダに解凍  
3. Python 3.x が必要（tkinter 標準搭載）

![Folder Structure](ここにフォルダ構成スクショのパス)

---

## Launch / 起動方法
1. Run `VideoAssist.py` with Python  
2. The following window will appear  
#
1. 解凍したフォルダ内の `VideoAssist.py` を Python で実行  
2. 以下のウィンドウが表示されます

![Launch Screen](ここに起動画面スクショのパス)

---

## User Interface / 画面説明

### Input Video File / 入力動画ファイル
- Select an existing MLT file  
- Path appears in the entry box  
- Use "Browse" to select file  

- 既存の MLT ファイルを選択  
- Entry にパスが表示されます  
- 「Browse」でファイル選択可能

![Input Video File](ここに入力動画ファイル欄スクショのパス)

### Subtitles CSV File / 字幕 CSV ファイル
- Select CSV file  
- Path appears in the entry box  
- Use "Browse" to select file  

- CSV ファイルを選択  
- Entry にパスが表示されます  
- 「Browse」でファイル選択可能

![Subtitles CSV File](ここに字幕CSVファイル欄スクショのパス)

### Playlist ID / プレイリスト番号
- Specify which playlist (from the bottom) to add subtitles  
- Default is `1`  

- 下から何番目のプレイリストに字幕を追加するか指定  
- 初期値は `1`

![Playlist ID](ここにPlaylist ID欄スクショのパス)

### Run Button / 実行ボタン
- Click "Add Subtitles" to start  
- Output `{original_filename}_subtitled.mlt` will be generated  

- 「Add Subtitles」をクリックすると処理開始  
- 出力ファイル `{既存のファイル名}_subtitled.mlt` が生成されます

![Run Button](ここに実行ボタンスクショのパス)

---

## How to Use / 操作手順
1. Select existing MLT file in "Input Video File"  
2. Select CSV file in "Subtitles CSV File"  
3. Enter playlist ID (from bottom)  
4. Click "Add Subtitles"  
5. Open generated MLT in Shotcut → subtitles appear in specified playlist  
#
1. 「Input Video File」で既存 MLT ファイルを指定  
2. 「Subtitles CSV File」で CSV を指定  
3. 「Playlist ID」を入力（下から数える位置）  
4. 「Add Subtitles」をクリック  
5. 出力された MLT を Shotcut で開くと、指定プレイリストに字幕が追加されます

![Shotcut Preview](ここに生成されたMLTをShotcutで開いた画面スクショのパス)

---

## Notes / 注意事項
- CSV must have 1 column, 1 row = 1 subtitle  
- Each subtitle is added as a 2-second clip  
- Original MLT file is not overwritten  

- CSV は1列のみ、1行＝1字幕  
- 1字幕＝2秒間で追加されます  
- 元の MLT ファイルは上書きされません
