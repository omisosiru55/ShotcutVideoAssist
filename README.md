mltpy

mltpy is a lightweight Python wrapper for generating and editing MLT XML.
MLT is the video editing engine used by Shotcut
 and the melt command.
With mltpy, you can automate video editing tasks in Python without manually writing XML.

Features

Intuitive Python API

Add producers (clips)

Apply filters

Save projects and render with melt

Installation

(if not on PyPI yet, install from GitHub)

git clone https://github.com/yourname/mltpy.git
cd mltpy
pip install -e .

Usage
from mltpy import Project

# Create a project
proj = Project(profile="hdv_1080_25p")

# Add a clip
pid = proj.add_producer("video.mp4", in_point=0, out_point=100)

# Apply a filter
proj.add_filter(pid, "affine", scale_x=0.5, scale_y=0.5)

# Save to XML
proj.save("output.mlt")


The .mlt file can be opened in Shotcut or rendered directly using melt:

melt output.mlt -consumer avformat:out.mp4 vcodec=libx264 acodec=aac

License

MIT

mltpy

mltpy は、MLT XML を Python から簡単に生成・編集できるラッパーライブラリです。
MLT は Shotcut
 や melt コマンドで使われる動画編集エンジンであり、
本ライブラリを使うことで XML を直接書かずにスクリプトで編集操作を自動化できます。

特徴

Python らしい直感的な API

プロデューサー（クリップ）の追加

フィルタの適用

プロジェクトの保存と melt でのレンダリング

インストール

（まだPyPI公開前の場合は GitHubインストール例）

git clone https://github.com/yourname/mltpy.git
cd mltpy
pip install -e .

使い方
from mltpy import Project

# プロジェクト作成
proj = Project(profile="hdv_1080_25p")

# 素材を追加
pid = proj.add_producer("video.mp4", in_point=0, out_point=100)

# フィルタを追加
proj.add_filter(pid, "affine", scale_x=0.5, scale_y=0.5)

# XML保存
proj.save("output.mlt")


保存した .mlt ファイルは Shotcut で読み込んだり、以下のように melt コマンドでレンダリング可能です：

melt output.mlt -consumer avformat:out.mp4 vcodec=libx264 acodec=aac

ライセンス

MIT
