
import argparse
from mltpy.editor import MLTEditor
from mltpy import MLTDataPackager
from dotenv import load_dotenv
import os

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
            '--wrap-max-length',
            type=int,
            default=90,
            help='Maximum length for wrapped lines / '
                 '折り返し処理する行の最大長'
        )
        
        parser.add_argument(
            '--wrap-dynamictext',
            action='store_true',
            help='Wrap long simple text lines to specified max length / '
                 '長いシンプルテキストの行を指定した最大長で折り返し処理する'
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

        parser.add_argument(
            '--cloud-render',
            action='store_true',
            help='Render on cloud / クラウドでレンダリングする'
        )

        return parser.parse_args(args)

class CLIApp:
    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def run(self):
        editor = MLTEditor(self.args.input_path)

        if self.args.wrap_subtitles:
            editor.wrap_srt_lines(max_length=self.args.wrap_max_length, force_wrap=self.args.force_wrap)

        if self.args.wrap_dynamictext:
            editor.wrap_dynamictext_lines(max_length=self.args.wrap_max_length, force_wrap=self.args.force_wrap)

        if self.args.translate_dynamictext:
            editor.translate_dynamictext(from_lang=self.args.translate_from, to_lang=self.args.translate_to)

        if self.args.cloud_render:
            packager = MLTDataPackager(self.args.input_path)
            zip_path = packager.prepare_zip()  # data.zip を生成
            #print(zip_path)
            #status, text = packager.upload("http://wkimono.home/upload")  # アップロード
            #print(zip_path, status, text)
        else:
            editor.save()

def main(args=None):
    load_dotenv()  # .envファイルから環境変数を読み込む
    # GCLOUD_PROJECT_IDが設定されているか確認
    if not os.getenv("GCLOUD_PROJECT_ID"):
        print("エラー: 環境変数 GCLOUD_PROJECT_ID が設定されていません。")
        print(".env ファイルを作成し、GCLOUD_PROJECT_ID='your-project-id' と記述してください。")
        return # 環境変数がなければ処理を中断

    parsed_args = CLIParser.parse_arguments(args)
    app = CLIApp(parsed_args)
    app.run()

if __name__ == "__main__":
    main()