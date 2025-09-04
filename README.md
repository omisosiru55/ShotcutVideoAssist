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

<img width="763" height="212" alt="スクリーンショット 2025-09-04 200934" src="https://github.com/user-attachments/assets/f3ba9f74-3df6-466d-a8c5-292f01efd578" />

---

## Launch / 起動方法
1. Run `VideoAssist.py` with Python  
2. The following window will appear  
#
1. 解凍したフォルダ内の `VideoAssist.py` を Python で実行  
2. 以下のウィンドウが表示されます

<img width="544" height="506" alt="image" src="https://github.com/user-attachments/assets/09941b35-93e1-4e65-8585-72bbf5a7eb02" />
<img width="537" height="505" alt="image" src="https://github.com/user-attachments/assets/ad204723-a31c-49f6-b5e2-a57407d2dd52" />


---

## User Interface / 画面説明

### Input Video File / 入力動画ファイル
- Select an existing MLT file  
- Path appears in the entry box  
- Use "Browse" to select file  

- 既存の MLT ファイルを選択  
- Entry にパスが表示されます  
- 「Browse」でファイル選択可能

<img width="505" height="352" alt="image" src="https://github.com/user-attachments/assets/c8aa941c-2277-4379-8833-fb7a7a7ad450" />
<img width="506" height="347" alt="image" src="https://github.com/user-attachments/assets/b23e257c-5d11-445f-bc90-9a9f194fd42f" />

### Subtitles CSV File / 字幕 CSV ファイル
- Select CSV file  
- Path appears in the entry box  
- Use "Browse" to select file  

- CSV ファイルを選択  
- Entry にパスが表示されます  
- 「Browse」でファイル選択可能

<img width="509" height="346" alt="image" src="https://github.com/user-attachments/assets/699ad67b-f2fc-463b-bb50-56cdffbaa26a" />
<img width="509" height="346" alt="image" src="https://github.com/user-attachments/assets/b86fa2bb-109b-4d80-a966-2388daa060ba" />

### Playlist ID / プレイリスト番号
- Specify which playlist (from the bottom) to add subtitles  
- Default is `1`  

- 下から何番目のプレイリストに字幕を追加するか指定  
- 初期値は `1`

<img width="505" height="346" alt="image" src="https://github.com/user-attachments/assets/9f6b1b27-6423-4227-9333-6a495f7d6a1e" />

### Run Button / 実行ボタン
- Click "Add Subtitles" to start  
- Output `{original_filename}_subtitled.mlt` will be generated  

- 「Add Subtitles」をクリックすると処理開始  
- 出力ファイル `{既存のファイル名}_subtitled.mlt` が生成されます

<img width="505" height="345" alt="image" src="https://github.com/user-attachments/assets/bf70df03-abdf-41e7-9d68-ad73d6f71d41" />

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

<img width="1683" height="1091" alt="image" src="https://github.com/user-attachments/assets/0098f143-ed82-40e4-9d00-d2eeb8c5c2da" />

---

## Notes / 注意事項
- CSV must have 1 column, 1 row = 1 subtitle  
- Each subtitle is added as a 2-second clip  
- Original MLT file is not overwritten  

- CSV は1列のみ、1行＝1字幕  
- 1字幕＝2秒間で追加されます  
- 元の MLT ファイルは上書きされません
