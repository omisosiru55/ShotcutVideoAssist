<img width="494" height="413" alt="image" src="https://github.com/user-attachments/assets/9dfe8255-a713-4b78-bebf-a6b59b75f867" />

# mltpy

A Python library and GUI for editing MLT (Media Lovin' Toolkit) files used by video editing applications like Shotcut and OpenShot.

## Features

- **Batch wrap**: wrap SRT and simple text (dynamictext) with your prefered characters.

## Installation
Put the exe file onto any folder of your laptop/machine.

### Requirements

- Python 3.8+
- lxml >= 4.6.0

### Basic Usage
1. Wrap Subtitles or rap Simple Text from rocessing Options.
2. Choose Force Wrap if you want to make a new line regardless of space.
3. Specify character number if you want to change the default till this tool make a new line.
4. Choose your mlt file.
5. Run to execute.
6. Check a new file, which will be created at the same folder as the original mlt file.

### How to Build
This application can be built using pyinstaller.

Bash

pip install pyinstaller
pyinstaller --onefile --noconsole -n ShotcutMLTToolbox mltpy/gui.py

Once the build is complete, the executable file will be generated in the dist directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for working with MLT framework files
- Compatible with Shotcut, OpenShot, and other MLT-based editors
- Uses OpenCV for media file processing


### Cloud Rendering 

Package an existing .mlt project into a portable zip and upload it to your Flask cloud renderer.

- What the packager does:
  - Parse the .mlt as XML
  - Rewrite all `producer > property[name="resource"]` and `chain > property[name="resource"]` file paths to `data/<filename>`
  - Collect those files into `data.zip` under `data/`
  - Save a modified MLT as `cloud_rendering.mlt` and include it in the zip
  - Optionally POST the zip to your server (default: `http://wkimono.home/upload`)

CLI example:

```bash
mltpy --input-path C:\\Users\\user\\Videos\\shotcut\\20250912test\\test1.mlt --cloud-render
```

Programmatic example:

```python
from mltpy import MLTDataPackager

packager = MLTDataPackager(r"C:\\Users\\user\\Videos\\shotcut\\20250912test\\test1.mlt")
zip_path = packager.prepare_zip()
status, text = packager.upload("http://wkimono.home/upload")
print(zip_path, status, text)
```

Server endpoints:
- `POST /upload` (header `X-Filename: data.zip`, content-type `application/octet-stream`)
- Optional: `GET /status/<unique_id>`, `GET /download/<unique_id>`

---

# mltpy

MLT（Media Lovin' Toolkit）ファイルを編集するための Python ライブラリ＆GUIツールです。  
Shotcut や OpenShot などの動画編集アプリケーションで使用できます。

## 特徴

- **一括ラップ機能**: SRTやシンプルなテキスト（dynamictext）を、好みの文字数で自動的に折り返します。

## インストール

exeファイルをパソコン内の任意のフォルダに置いてください。

### 必要環境

- Python 3.8 以上  
- lxml >= 4.6.0  

## 基本的な使い方

1. 処理オプションから「字幕を折り返す」または「シンプルテキストを折り返す」を選択します。  
2. 「強制改行」を選ぶと、スペースに関係なく指定の文字数で改行されます。  
3. デフォルトの文字数を変更したい場合は、改行する文字数を指定してください。  
4. 対象となる mlt ファイルを選択します。  
5. 実行を押して処理を開始します。  
6. 元の mlt ファイルと同じフォルダに新しいファイルが作成されます。  

## ビルド方法
このアプリケーションは pyinstaller を使用してビルドできます。

Bash

pip install pyinstaller
pyinstaller --onefile --noconsole -n ShotcutMLTToolbox mltpy/gui.py

ビルドが完了すると、dist ディレクトリ内に実行ファイルが生成されます。

## 貢献

1. リポジトリをフォーク
2. 機能ブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add amazing feature'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを開く

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 謝辞

- MLT フレームワークファイルの操作用に構築
- Shotcut、OpenShot、その他の MLT ベースのエディタと互換性があります
- メディアファイル処理に OpenCV を使用

#### クラウドレンダリング
手元の .mlt プロジェクトを ZIP にまとめ、Flask のクラウドレンダラーへアップロードできます。

- パッケージャの処理内容:
  - .mlt を XML として解析
  - `producer > property[name="resource"]` と `chain > property[name="resource"]` のファイルパスを `data/<ファイル名>` に書き換え
  - 実ファイルを ZIP 内の `data/` 配下へ格納
  - 修正版 MLT を `cloud_rendering.mlt` として保存し、ZIP に含める
  - 必要に応じて ZIP をサーバ（既定: `http://wkimono.home/upload`）に POST

CLI 例:

```bash
mltpy --input-path C:\\Users\\user\\Videos\\shotcut\\20250912test\\test1.mlt --cloud-render
```

Python からの使用例:

```python
from mltpy import MLTDataPackager

packager = MLTDataPackager(r"C:\\Users\\user\\Videos\\shotcut\\20250912test\\test1.mlt")
zip_path = packager.prepare_zip()
status, text = packager.upload("http://wkimono.home/upload")
print(zip_path, status, text)
```

サーバ側の主なエンドポイント:
- `POST /upload`: `data.zip` を送信（ヘッダー `X-Filename: data.zip`、Content-Type は `application/octet-stream`）
- 任意: `GET /status/<unique_id>` で進行状況、`GET /download/<unique_id>` で完成動画をダウンロード
