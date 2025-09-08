"""
mltpy.media - メディアファイル関連のユーティリティクラス

動画ファイル、画像ファイルの情報取得や操作を行うクラス群
"""

from pathlib import Path
import re
import cv2
import numpy as np
from typing import Optional, Tuple, Union

from .exceptions import (
    MediaFileNotFoundError,
    MediaFileIOError, 
    InvalidMediaFormatError,
    InvalidDurationError
)


class MediaUtils:
    """メディアファイル関連のユーティリティクラス"""
    
    # サポートする画像形式
    SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp"}
    
    # サポートする動画形式  
    SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"}
    
    @staticmethod
    def get_video_duration(video_path: Union[str, Path], speed: float = 1.0) -> str:
        """
        動画の長さを取得（00:00:00.000形式）
        
        Args:
            video_path: 動画ファイルのパス
            speed: 再生速度倍率（例: 4なら4倍速 → 長さ1/4）
            
        Returns:
            HH:MM:SS.mmm形式の時間文字列
            
        Raises:
            MediaFileNotFoundError: ファイルが見つからない場合
            MediaFileIOError: ファイルを開けない場合
            InvalidDurationError: 無効な速度が指定された場合
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise MediaFileNotFoundError(video_path)
        
        if speed <= 0:
            raise InvalidDurationError(f"無効な速度: {speed}")
        
        # VideoCaptureオブジェクトを作成
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise MediaFileIOError(video_path, "OpenCVで動画ファイルを開けませんでした")
        
        try:
            # 総フレーム数とFPSを取得
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            if fps <= 0:
                raise MediaFileIOError(video_path, f"無効なFPS値: {fps}")
            
            # 動画の長さを計算
            duration_seconds = (frame_count / fps) / speed
            
        finally:
            cap.release()
        
        # 秒を「時:分:秒.ミリ秒」に変換
        return MediaUtils._seconds_to_timestring(duration_seconds)
    
    @staticmethod
    def get_media_path_from_resource(resource_elem) -> Optional[Path]:
        """
        プロデューサータグ内のリソース要素からパスを抽出
        
        Args:
            resource_elem: XMLのresource要素
            
        Returns:
            Pathオブジェクト、または見つからない場合はNone
        """
        if resource_elem is None or not resource_elem.text:
            return None
        
        resource = resource_elem.text.strip()
        
        # "4:C:/..." のような接頭辞を除去
        resource = re.sub(r'^\d+:', '', resource)
        
        # スラッシュをWindows用に修正
        media_path = Path(resource.replace("/", "\\")).resolve()
        
        if not media_path.exists():
            print(f"警告: ファイルが見つかりません {media_path}")
            return None
        
        return media_path
    
    @staticmethod
    def get_media_size(file_path: Union[str, Path]) -> Tuple[int, int]:
        """
        動画または静止画の幅・高さを取得
        
        Args:
            file_path: メディアファイルのパス
            
        Returns:
            (width, height) のタプル
            
        Raises:
            MediaFileNotFoundError: ファイルが見つからない場合
            MediaFileIOError: ファイルを読み込めない場合
            InvalidMediaFormatError: サポートされていない形式の場合
        """
        path = Path(file_path)
        
        if not path.exists():
            raise MediaFileNotFoundError(path)
        
        ext = path.suffix.lower()
        
        # 静止画の場合
        if ext in MediaUtils.SUPPORTED_IMAGE_FORMATS:
            try:
                img = MediaUtils._imread_unicode(str(path))
                if img is None:
                    raise MediaFileIOError(path, "画像を読み込めませんでした")
                height, width = img.shape[:2]
                return width, height
            except Exception as e:
                raise MediaFileIOError(path, f"画像処理エラー: {str(e)}")
        
        # 動画の場合
        elif ext in MediaUtils.SUPPORTED_VIDEO_FORMATS:
            cap = cv2.VideoCapture(str(path))
            if not cap.isOpened():
                raise MediaFileIOError(path, "OpenCVで動画ファイルを開けませんでした")
            
            try:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                if width <= 0 or height <= 0:
                    raise MediaFileIOError(path, f"無効な解像度: {width}x{height}")
                
                return width, height
            finally:
                cap.release()
        
        else:
            raise InvalidMediaFormatError(path, ext)
    
    @staticmethod
    def _imread_unicode(path: str):
        """
        Unicodeパス対応の画像読み込み
        OpenCVのimreadはUnicodeパスに対応していないため、numpyとcv2.imdecodeを使って読み込む
        """
        try:
            with open(path, "rb") as f:
                data = np.frombuffer(f.read(), np.uint8)
            return cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            return None
    
    @staticmethod
    def _seconds_to_timestring(duration_seconds: float) -> str:
        """秒数を HH:MM:SS.mmm 形式に変換"""
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = (seconds - int(seconds)) * 1000
        
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}"
    
    @staticmethod
    def validate_duration_format(duration_str: str) -> bool:
        """
        時間形式文字列の妥当性を検証
        
        Args:
            duration_str: HH:MM:SS.mmm形式の時間文字列
            
        Returns:
            有効な形式の場合True
        """
        pattern = r'^\d{2}:\d{2}:\d{2}\.\d{3}$'
        return bool(re.match(pattern, duration_str))
    
    @staticmethod
    def timestring_to_seconds(duration_str: str) -> float:
        """
        HH:MM:SS.mmm形式の時間文字列を秒数に変換
        
        Args:
            duration_str: HH:MM:SS.mmm形式の時間文字列
            
        Returns:
            秒数（float）
            
        Raises:
            InvalidDurationError: 無効な形式の場合
        """
        if not MediaUtils.validate_duration_format(duration_str):
            raise InvalidDurationError(duration_str)
        
        try:
            time_part, ms_part = duration_str.split('.')
            hours, minutes, seconds = map(int, time_part.split(':'))
            milliseconds = int(ms_part)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            return total_seconds
        
        except ValueError as e:
            raise InvalidDurationError(duration_str) from e
    
    @staticmethod
    def is_supported_format(file_path: Union[str, Path]) -> bool:
        """
        ファイルがサポートされている形式かチェック
        
        Args:
            file_path: ファイルパス
            
        Returns:
            サポートされている場合True
        """
        ext = Path(file_path).suffix.lower()
        return ext in (MediaUtils.SUPPORTED_IMAGE_FORMATS | MediaUtils.SUPPORTED_VIDEO_FORMATS)
    
    @staticmethod
    def get_media_type(file_path: Union[str, Path]) -> str:
        """
        メディアファイルの種類を判定
        
        Args:
            file_path: ファイルパス
            
        Returns:
            'image', 'video', 'unknown' のいずれか
        """
        ext = Path(file_path).suffix.lower()
        
        if ext in MediaUtils.SUPPORTED_IMAGE_FORMATS:
            return 'image'
        elif ext in MediaUtils.SUPPORTED_VIDEO_FORMATS:
            return 'video'
        else:
            return 'unknown'
