# mltpy

A Python library for editing MLT (Media Lovin' Toolkit) files used by video editing applications like Shotcut and OpenShot.

## Features

- **Batch wrap**: wrap SRT and simple text (dynamictext) with your prefered characters.

## Installation
Put the exe file onto any folder of your laptop/machine.

### Requirements

- Python 3.8+
- lxml >= 4.6.0

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


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for working with MLT framework files
- Compatible with Shotcut, OpenShot, and other MLT-based editors
- Uses OpenCV for media file processing

---


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
