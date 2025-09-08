"""
mltpy.exceptions - カスタム例外クラス

MLTファイル処理中に発生する様々なエラーを適切に分類するための例外クラス群
"""


class MLTError(Exception):
    """mltpyライブラリの基本例外クラス"""
    pass


class MLTFileNotFoundError(MLTError):
    """MLTファイルが見つからない場合の例外"""
    def __init__(self, file_path):
        self.file_path = file_path
        super().__init__(f"MLTファイルが見つかりません: {file_path}")


class MLTParseError(MLTError):
    """MLTファイルの解析に失敗した場合の例外"""
    def __init__(self, file_path, details=None):
        self.file_path = file_path
        self.details = details
        message = f"MLTファイルの解析に失敗しました: {file_path}"
        if details:
            message += f" ({details})"
        super().__init__(message)


class MLTPlaylistNotFoundError(MLTError):
    """指定したプレイリストIDが見つからない場合の例外"""
    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        super().__init__(f"プレイリスト ID {playlist_id} が見つかりません")


class MLTOutputPathError(MLTError):
    """出力パス関連のエラー"""
    def __init__(self, message, path=None):
        self.path = path
        super().__init__(message)


class MediaFileError(MLTError):
    """メディアファイル関連のエラー基底クラス"""
    pass


class MediaFileNotFoundError(MediaFileError):
    """メディアファイルが見つからない場合の例外"""
    def __init__(self, file_path):
        self.file_path = file_path
        super().__init__(f"メディアファイルが見つかりません: {file_path}")


class MediaFileIOError(MediaFileError):
    """メディアファイルの読み込みに失敗した場合の例外"""
    def __init__(self, file_path, details=None):
        self.file_path = file_path
        self.details = details
        message = f"メディアファイルの読み込みに失敗しました: {file_path}"
        if details:
            message += f" ({details})"
        super().__init__(message)


class InvalidMediaFormatError(MediaFileError):
    """サポートされていないメディアフォーマットの場合の例外"""
    def __init__(self, file_path, format_type=None):
        self.file_path = file_path
        self.format_type = format_type
        message = f"サポートされていないメディアフォーマットです: {file_path}"
        if format_type:
            message += f" (フォーマット: {format_type})"
        super().__init__(message)


class InvalidDurationError(MLTError):
    """無効な時間形式の場合の例外"""
    def __init__(self, duration_str):
        self.duration_str = duration_str
        super().__init__(f"無効な時間形式です: {duration_str} (正しい形式: HH:MM:SS.mmm)")


class ProducerIDError(MLTError):
    """プロデューサーID関連のエラー"""
    def __init__(self, message, producer_id=None):
        self.producer_id = producer_id
        super().__init__(message)
