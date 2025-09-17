"""
mltpy - Python library for editing MLT files

MLT (Media Looping Technology) files are XML-based project files used by 
video editing applications like Shotcut and OpenShot.

Basic usage:
    from mltpy import MLTEditor
    
    # Create editor instance
    editor = MLTEditor("project.mlt")
    
    # Add clips
    editor.add_video_clip("video.mp4")
    editor.add_image_clip("image.jpg", duration="00:00:05.000")
    editor.add_text_overlay("Hello World!")
    
    # Save
    editor.save("output.mlt")
"""

from .editor import MLTEditor
from .packager import MLTDataPackager
from .media import MediaUtils
from .cli import CLIParser
from .exceptions import (
    MLTError,
    MLTFileNotFoundError,
    MLTParseError,
    MediaFileError
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# パッケージレベルでエクスポートするクラス/関数を定義
__all__ = [
    "MLTEditor",
    "MLTDataPackager",
    "MediaUtils", 
    "CLIParser",
    "CLIApp",
    "MLTError",
    "MLTFileNotFoundError", 
    "MLTParseError",
    "MLTPlaylistNotFoundError",
    "MLTOutputPathError",
    "MediaFileError",
    "MediaFileNotFoundError",
    "MediaFileIOError", 
    "InvalidMediaFormatError",
    "InvalidDurationError",
    "ProducerIDError",
]