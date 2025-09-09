
import argparse
from .editor import MLTEditor

class CLIParser:
    @staticmethod
    def parse_arguments(args=None):
        
        parser = argparse.ArgumentParser()
        
        parser.add_argument(
            '--input-path', 
            type=str, 
            required=True,
            help='Path to the MLT file to edit / 編集対象のMLTファイルへのパス'
        )
        
        parser.add_argument(
            '--playlist-id',
            type=int,
            default=0,
            help='Target playlist ID (default: 0) / 操作対象のプレイリストID（デフォルト: 4）'
        )
        
        parser.add_argument(
            '--wrap-subtitles',
            action='store_true',
            help='Wrap long subtitle lines to specified max length / '
                 '長い字幕行を指定した最大長で折り返し処理する'
        )
        
        parser.add_argument(
            '--data-dir',
            type=str,
            default=r'C:\data',
            help='Path to data directory for adding clips (default: C:\\data) / '
                 'クリップを追加するデータディレクトリのパス（デフォルト: C:\\data）'
        )
        
        return parser.parse_args(args)

class CLIApp:
    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def run(self):
        editor = MLTEditor(self.args.input_path, self.args.playlist_id)
        editor.save()

def main(args=None):
    parsed_args = CLIParser.parse_arguments(args)
    app = CLIApp(parsed_args)
    app.run()

if __name__ == "__main__":
    main()