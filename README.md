# mltpy

A Python library for editing MLT (Media Looping Technology) files used by video editing applications like Shotcut and OpenShot.

## Features

- **Easy MLT File Editing**: Load, modify, and save MLT project files programmatically
- **Video Clip Management**: Add video clips with speed control and custom properties
- **Image Clip Support**: Insert static images with configurable duration
- **Text Overlay Creation**: Add dynamic text overlays with customizable styling
- **Media Utilities**: Get video duration, media dimensions, and format validation
- **Command Line Interface**: Use mltpy from the command line for batch operations
- **Type Hints**: Full type annotation support for better development experience

## Installation

### From GitHub (Recommended for now)

```bash
pip install git+https://github.com/yourusername/mltpy.git
```

### For Development

```bash
git clone https://github.com/yourusername/mltpy.git
cd mltpy
pip install -e .
```

### Requirements

- Python 3.8+
- lxml >= 4.6.0
- opencv-python >= 4.5.0
- numpy >= 1.21.0

## Quick Start

### Basic Usage

```python
from mltpy import MLTEditor

# Load an existing MLT project
editor = MLTEditor("project.mlt", playlist_id=4)

# Set output path
editor.set_output_path("processed")

# Add video clip with 1.5x speed
editor.add_video_clip("video.mp4", speed=1.5)

# Add image clip for 5 seconds
editor.add_image_clip("image.jpg", duration="00:00:05.000")

# Add text overlay
editor.add_text_overlay("Hello World!", duration="00:00:03.000")

# Save the modified project
editor.save()
```

### Media Utilities

```python
from mltpy import MediaUtils

# Get video duration
duration = MediaUtils.get_video_duration("video.mp4")
print(f"Duration: {duration}")  # Output: 00:01:30.500

# Get media dimensions
width, height = MediaUtils.get_media_size("image.jpg")
print(f"Size: {width}x{height}")

# Check supported formats
is_supported = MediaUtils.is_supported_format("file.mp4")
media_type = MediaUtils.get_media_type("file.jpg")  # Returns: 'image'
```

### Command Line Interface

```bash
# Basic usage
mltpy --input-path project.mlt --output-suffix processed

# Add video clips
mltpy --input-path project.mlt --add-video video1.mp4 --add-video video2.mp4 --speed 2.0

# Add image clips  
mltpy --input-path project.mlt --add-image image1.jpg --add-image image2.png --duration 00:00:05.000

# Add text overlays
mltpy --input-path project.mlt --add-text "Title" --add-text "Subtitle"

# Verbose output and dry run
mltpy --input-path project.mlt --add-video clip.mp4 --verbose --dry-run
```

## API Reference

### MLTEditor Class

The main class for editing MLT files.

#### Constructor

```python
MLTEditor(input_path: Union[str, Path], playlist_id: int = 4)
```

- `input_path`: Path to the MLT file to edit
- `playlist_id`: Target playlist ID (default: 4)

#### Methods

- `set_output_path(suffix: str = "edited") -> Path`: Set the output file path
- `add_video_clip(file_path, speed=1.0, extra_properties=None)`: Add a video clip
- `add_image_clip(file_path, duration="00:00:05.000", extra_properties=None)`: Add an image clip
- `add_text_overlay(text, duration="00:01:00.000", background_color="#ffffff")`: Add text overlay
- `save(output_path=None)`: Save the MLT file
- `get_producers_info() -> list`: Get information about all producers
- `remove_producer(producer_id: str) -> bool`: Remove a producer by ID

#### Properties

- `project_size -> Tuple[int, int]`: Get project resolution (width, height)

### MediaUtils Class

Utility functions for media file operations.

#### Static Methods

- `get_video_duration(video_path, speed=1.0) -> str`: Get video duration in HH:MM:SS.mmm format
- `get_media_size(file_path) -> Tuple[int, int]`: Get media dimensions
- `is_supported_format(file_path) -> bool`: Check if file format is supported
- `get_media_type(file_path) -> str`: Get media type ('image', 'video', 'unknown')
- `validate_duration_format(duration_str) -> bool`: Validate time format string
- `timestring_to_seconds(duration_str) -> float`: Convert time string to seconds

### Exception Classes

- `MLTError`: Base exception for all mltpy errors
- `MLTFileNotFoundError`: MLT file not found
- `MLTParseError`: MLT file parsing failed
- `MediaFileNotFoundError`: Media file not found
- `MediaFileIOError`: Media file read error
- `InvalidDurationError`: Invalid time format

## Examples

See the `examples/` directory for more detailed usage examples:

- `examples/basic_usage.py`: Basic MLT editing operations
- `examples/video_processing.py`: Advanced video processing
- `examples/batch_convert.py`: Batch processing multiple files

## Supported Formats

### Video Formats
- MP4, MOV, AVI, MKV, WMV, FLV, WebM

### Image Formats  
- JPG, JPEG, PNG, BMP, TIFF, GIF, WebP

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black mltpy/
flake8 mltpy/
```

### Type Checking

```bash
mypy mltpy/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for working with MLT framework files
- Compatible with Shotcut, OpenShot, and other MLT-based editors
- Uses OpenCV for media file processing

---

# mltpy

Shotcut や OpenShot などの動画編集アプリケーションで使用される MLT（Media Looping Technology）ファイルを編集するための Python ライブラリです。

## 特徴

- **簡単なMLTファイル編集**: MLT プロジェクトファイルをプログラムで読み込み、変更、保存
- **動画クリップ管理**: 速度制御とカスタムプロパティ付きで動画クリップを追加
- **画像クリップ対応**: 設定可能な表示時間で静止画を挿入
- **テキストオーバーレイ作成**: カスタマイズ可能なスタイリングでダイナミックテキストオーバーレイを追加
- **メディアユーティリティ**: 動画の長さ、メディア寸法、形式検証の取得
- **コマンドラインインターフェース**: バッチ操作用のコマンドラインから mltpy を使用
- **型ヒント**: より良い開発体験のための完全な型注釈サポート

## インストール

### GitHub から（現在推奨）

```bash
pip install git+https://github.com/yourusername/mltpy.git
```

### 開発用

```bash
git clone https://github.com/yourusername/mltpy.git
cd mltpy
pip install -e .
```

### 要件

- Python 3.8+
- lxml >= 4.6.0
- opencv-python >= 4.5.0
- numpy >= 1.21.0

## クイックスタート

### 基本的な使用方法

```python
from mltpy import MLTEditor

# 既存のMLTプロジェクトを読み込み
editor = MLTEditor("project.mlt", playlist_id=4)

# 出力パスを設定
editor.set_output_path("processed")

# 1.5倍速で動画クリップを追加
editor.add_video_clip("video.mp4", speed=1.5)

# 5秒間の画像クリップを追加
editor.add_image_clip("image.jpg", duration="00:00:05.000")

# テキストオーバーレイを追加
editor.add_text_overlay("Hello World!", duration="00:00:03.000")

# 変更されたプロジェクトを保存
editor.save()
```

### メディアユーティリティ

```python
from mltpy import MediaUtils

# 動画の長さを取得
duration = MediaUtils.get_video_duration("video.mp4")
print(f"Duration: {duration}")  # 出力: 00:01:30.500

# メディアの寸法を取得
width, height = MediaUtils.get_media_size("image.jpg")
print(f"Size: {width}x{height}")

# サポートされている形式をチェック
is_supported = MediaUtils.is_supported_format("file.mp4")
media_type = MediaUtils.get_media_type("file.jpg")  # 戻り値: 'image'
```

### コマンドラインインターフェース

```bash
# 基本的な使用方法
mltpy --input-path project.mlt --output-suffix processed

# 動画クリップを追加
mltpy --input-path project.mlt --add-video video1.mp4 --add-video video2.mp4 --speed 2.0

# 画像クリップを追加
mltpy --input-path project.mlt --add-image image1.jpg --add-image image2.png --duration 00:00:05.000

# テキストオーバーレイを追加
mltpy --input-path project.mlt --add-text "タイトル" --add-text "サブタイトル"

# 詳細出力とドライラン
mltpy --input-path project.mlt --add-video clip.mp4 --verbose --dry-run
```

## API リファレンス

### MLTEditor クラス

MLT ファイル編集のメインクラスです。

#### コンストラクタ

```python
MLTEditor(input_path: Union[str, Path], playlist_id: int = 4)
```

- `input_path`: 編集するMLTファイルへのパス
- `playlist_id`: 対象のプレイリストID（デフォルト: 4）

#### メソッド

- `set_output_path(suffix: str = "edited") -> Path`: 出力ファイルパスを設定
- `add_video_clip(file_path, speed=1.0, extra_properties=None)`: 動画クリップを追加
- `add_image_clip(file_path, duration="00:00:05.000", extra_properties=None)`: 画像クリップを追加
- `add_text_overlay(text, duration="00:01:00.000", background_color="#ffffff")`: テキストオーバーレイを追加
- `save(output_path=None)`: MLTファイルを保存
- `get_producers_info() -> list`: すべてのプロデューサーの情報を取得
- `remove_producer(producer_id: str) -> bool`: IDでプロデューサーを削除

#### プロパティ

- `project_size -> Tuple[int, int]`: プロジェクト解像度を取得（幅、高さ）

### MediaUtils クラス

メディアファイル操作用のユーティリティ関数です。

#### 静的メソッド

- `get_video_duration(video_path, speed=1.0) -> str`: HH:MM:SS.mmm形式で動画の長さを取得
- `get_media_size(file_path) -> Tuple[int, int]`: メディアの寸法を取得
- `is_supported_format(file_path) -> bool`: ファイル形式がサポートされているかチェック
- `get_media_type(file_path) -> str`: メディアタイプを取得（'image'、'video'、'unknown'）
- `validate_duration_format(duration_str) -> bool`: 時間形式文字列を検証
- `timestring_to_seconds(duration_str) -> float`: 時間文字列を秒数に変換

### 例外クラス

- `MLTError`: すべてのmltpyエラーの基本例外
- `MLTFileNotFoundError`: MLTファイルが見つからない
- `MLTParseError`: MLTファイルの解析に失敗
- `MediaFileNotFoundError`: メディアファイルが見つからない
- `MediaFileIOError`: メディアファイル読み込みエラー
- `InvalidDurationError`: 無効な時間形式

## 使用例

詳細な使用例については `examples/` ディレクトリを参照してください：

- `examples/basic_usage.py`: 基本的なMLT編集操作
- `examples/video_processing.py`: 高度な動画処理
- `examples/batch_convert.py`: 複数ファイルのバッチ処理

## サポートされている形式

### 動画形式
- MP4、MOV、AVI、MKV、WMV、FLV、WebM

### 画像形式
- JPG、JPEG、PNG、BMP、TIFF、GIF、WebP

## 開発

### テストの実行

```bash
pip install -e ".[dev]"
pytest
```

### コードフォーマット

```bash
black mltpy/
flake8 mltpy/
```

### 型チェック

```bash
mypy mltpy/
```

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