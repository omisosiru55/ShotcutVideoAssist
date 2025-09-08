"""
mltpy.cli - コマンドライン インターフェース

mltpyをコマンドラインから使用するためのクラス群
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from .editor import MLTEditor
from .media import MediaUtils
from .exceptions import MLTError


class CLIParser:
    """コマンドライン引数の解析クラス"""
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """
        argparseパーサーを作成
        
        Returns:
            設定済みのArgumentParserオブジェクト
        """
        parser = argparse.ArgumentParser(
            description='MLTファイルの編集ツール - 動画、画像、テキストクリップの追加が可能',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用例:
  # 基本的な使用方法
  mltpy --input-path project.mlt --output-suffix processed
  
  # CSVから字幕を追加
  mltpy --input-path project.mlt --csv-path subtitles.csv --playlist-id 4
  
  # 動画クリップを追加
  mltpy --input-path project.mlt --add-video video.mp4 --speed 1.5
  
  # 画像クリップを追加
  mltpy --input-path project.mlt --add-image image.jpg --duration 00:00:05.000
            """
        )
        
        # 必須引数
        parser.add_argument(
            '--input-path', 
            type=str, 
            required=True,
            help='編集対象のMLTファイルへのパス'
        )
        
        # オプション引数 - 出力設定
        parser.add_argument(
            '--output-path',
            type=str,
            help='出力MLTファイルのパス（指定しない場合は自動生成）'
        )
        
        parser.add_argument(
            '--output-suffix',
            type=str,
            default='edited',
            help='出力ファイル名のサフィックス（デフォルト: edited）'
        )
        
        # オプション引数 - プレイリスト設定
        parser.add_argument(
            '--playlist-id',
            type=int,
            default=4,
            help='操作対象のプレイリストID（デフォルト: 4）'
        )
        
        # オプション引数 - CSV字幕追加
        parser.add_argument(
            '--csv-path',
            type=str,
            help='字幕情報を含むCSVファイルへのパス'
        )
        
        # オプション引数 - メディア追加
        parser.add_argument(
            '--add-video',
            type=str,
            action='append',
            help='追加する動画ファイルのパス（複数指定可能）'
        )
        
        parser.add_argument(
            '--add-image', 
            type=str,
            action='append',
            help='追加する画像ファイルのパス（複数指定可能）'
        )
        
        parser.add_argument(
            '--add-text',
            type=str,
            action='append',
            help='追加するテキスト（複数指定可能）'
        )
        
        # オプション引数 - メディア設定
        parser.add_argument(
            '--speed',
            type=float,
            default=1.0,
            help='動画の再生速度倍率（デフォルト: 1.0）'
        )
        
        parser.add_argument(
            '--duration',
            type=str,
            default='00:00:05.000',
            help='画像・テキストの表示時間（デフォルト: 00:00:05.000）'
        )
        
        # オプション引数 - データディレクトリ
        parser.add_argument(
            '--data-dir',
            type=str,
            default=r'C:\data',
            help='クリップを追加するデータディレクトリのパス（デフォルト: C:\\data）'
        )
        
        # オプション引数 - その他
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='詳細な出力を表示'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='実際のファイル変更を行わずに処理内容のみを表示'
        )
        
        return parser
    
    @staticmethod
    def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        コマンドライン引数を解析
        
        Args:
            args: 引数リスト（テスト用、通常はNone）
            
        Returns:
            解析済みの引数
        """
        parser = CLIParser.create_parser()
        return parser.parse_args(args)


class CLIApp:
    """コマンドラインアプリケーションのメインクラス"""
    
    def __init__(self, args: argparse.Namespace):
        """
        CLIアプリケーションを初期化
        
        Args:
            args: 解析済みのコマンドライン引数
        """
        self.args = args
        self.verbose = args.verbose
        
    def _log(self, message: str, force: bool = False):
        """ログ出力（verboseモード時またはforce=True時のみ）"""
        if self.verbose or force:
            print(message)
    
    def _validate_args(self):
        """引数の妥当性を検証"""
        # 入力ファイルの存在確認
        input_path = Path(self.args.input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"入力MLTファイルが見つかりません: {input_path}")
        
        # CSVファイルの存在確認
        if self.args.csv_path:
            csv_path = Path(self.args.csv_path)
            if not csv_path.exists():
                raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")
        
        # 動画ファイルの存在確認
        if self.args.add_video:
            for video_path in self.args.add_video:
                path = Path(video_path)
                if not path.exists():
                    raise FileNotFoundError(f"動画ファイルが見つかりません: {path}")
                if not MediaUtils.is_supported_format(path):
                    raise ValueError(f"サポートされていない動画形式です: {path}")
        
        # 画像ファイルの存在確認
        if self.args.add_image:
            for image_path in self.args.add_image:
                path = Path(image_path)
                if not path.exists():
                    raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")
                if not MediaUtils.is_supported_format(path):
                    raise ValueError(f"サポートされていない画像形式です: {path}")
        
        # 時間形式の検証
        if not MediaUtils.validate_duration_format(self.args.duration):
            raise ValueError(f"無効な時間形式です: {self.args.duration}")
        
        # 速度の検証
        if self.args.speed <= 0:
            raise ValueError(f"無効な速度です: {self.args.speed}")
    
    def run(self) -> int:
        """
        メイン処理を実行
        
        Returns:
            終了コード（0: 成功、1: エラー）
        """
        try:
            self._log("引数の検証中...")
            self._validate_args()
            
            self._log(f"MLTファイル読み込み中: {self.args.input_path}")
            editor = MLTEditor(self.args.input_path, self.args.playlist_id)
            
            # 出力パスの設定
            if self.args.output_path:
                editor.output_path = Path(self.args.output_path)
            else:
                output_path = editor.set_output_path(self.args.output_suffix)
                self._log(f"出力パス: {output_path}")
            
            # プロジェクト情報の表示
            width, height = editor.project_size
            self._log(f"プロジェクト解像度: {width}x{height}")
            
            # dry-runモード
            if self.args.dry_run:
                self._log("DRY-RUNモード: 実際のファイル変更は行いません", force=True)
            
            # 動画クリップの追加
            if self.args.add_video:
                for video_path in self.args.add_video:
                    self._log(f"動画クリップ追加: {video_path} (速度: {self.args.speed}x)")
                    if not self.args.dry_run:
                        editor.add_video_clip(video_path, speed=self.args.speed)
            
            # 画像クリップの追加
            if self.args.add_image:
                for image_path in self.args.add_image:
                    self._log(f"画像クリップ追加: {image_path} (時間: {self.args.duration})")
                    if not self.args.dry_run:
                        editor.add_image_clip(image_path, duration=self.args.duration)
            
            # テキストオーバーレイの追加
            if self.args.add_text:
                for text in self.args.add_text:
                    self._log(f"テキスト追加: '{text}' (時間: {self.args.duration})")
                    if not self.args.dry_run:
                        editor.add_text_overlay(text, duration=self.args.duration)
            
            # CSVから字幕追加（実装は別途必要）
            if self.args.csv_path:
                self._log(f"CSV字幕追加: {self.args.csv_path}")
                if not self.args.dry_run:
                    # TODO: CSV処理機能の実装
                    self._log("CSV処理機能は未実装です", force=True)
            
            # ファイル保存
            if not self.args.dry_run:
                self._log("ファイル保存中...")
                editor.save()
                self._log("処理完了", force=True)
            else:
                self._log("DRY-RUN完了", force=True)
            
            return 0
            
        except MLTError as e:
            print(f"MLTエラー: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"予期しないエラー: {e}", file=sys.stderr)
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1


def main(args: Optional[List[str]] = None) -> int:
    """
    メイン エントリーポイント
    
    Args:
        args: コマンドライン引数（テスト用）
        
    Returns:
        終了コード
    """
    try:
        parsed_args = CLIParser.parse_arguments(args)
        app = CLIApp(parsed_args)
        return app.run()
    except KeyboardInterrupt:
        print("\n処理が中断されました", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"致命的エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
