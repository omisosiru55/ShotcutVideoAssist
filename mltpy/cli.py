
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
            '--wrap-subtitles-max-length',
            type=int,
            default=None,
            help='Maximum length for wrapped subtitle lines / '
                 '折り返し処理する字幕行の最大長'
        )

        parser.add_argument(
            '--force-wrap',
            action='store_true',
            help='Force wrapping lines even without spaces, useful for languages like Chinese / スペースがない言語（中国語など）でも強制的に行を折り返す'
        )

        parser.add_argument(
            '--data-dir',
            type=str,
            default=r'C:\data',
            help='Path to data directory for adding clips (default: C:\\data) / '
                 'クリップを追加するデータディレクトリのパス（デフォルト: C:\\data）'
        )

        parser.add_argument(
            '--translate-dynamictext',
            action='store_true',
            help='Translate dynamictext filter arguments using Google Translate / '
                 'Google翻訳を使ってdynamictextフィルターの引数を翻訳する'
        )

        parser.add_argument(
            '--translate-from',
            type=str,
            default='en',
            help='language to translate from'
        )

        parser.add_argument(
            '--translate-to',
            type=str,
            default='ja',
            help='language to translate to'
        )

        return parser.parse_args(args)

class CLIApp:
    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def run(self):
        editor = MLTEditor(self.args.input_path)

        if self.args.wrap_subtitles:
            if self.args.wrap_subtitles_max_length is None:
                editor.wrap_srt_lines(force_wrap=self.args.force_wrap)
                editor.set_output_path("wrapped")
            else:
                editor.wrap_srt_lines(max_length=self.args.wrap_subtitles_max_length, force_wrap=self.args.force_wrap)
                editor.set_output_path(f"wrapped{self.args.wrap_subtitles_max_length}")


        editor.save()

def main(args=None):
    parsed_args = CLIParser.parse_arguments(args)
    app = CLIApp(parsed_args)
    app.run()

if __name__ == "__main__":
    main()