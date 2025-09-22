from google.cloud import translate
import os
import json
from dotenv import load_dotenv

class GoogleTranslator:
    def __init__(self, from_language="auto", target_language="en", max_translations=1000):
        """
        from_language: 翻訳元の言語（'auto'で自動検出）
        target_language: 翻訳先の言語
        max_translations: 最大翻訳回数。超えると原文を返す
        """
        # 環境変数を読み込み
        load_dotenv()
        
        # GOOGLE_APPLICATION_CREDENTIALSからproject_idを取得
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise ValueError("Environment variable GOOGLE_APPLICATION_CREDENTIALS is not set.\nPlease set GOOGLE_APPLICATION_CREDENTIALS to the path of your Google Cloud credentials JSON file. 環境変数 GOOGLE_APPLICATION_CREDENTIALS が設定されていません。\nGoogle Cloud認証情報JSONファイルのパスを設定してください。")
        
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                credentials_data = json.load(f)
                self.project_id = credentials_data.get('project_id')
                if not self.project_id:
                    raise ValueError("project_id not found in credentials file. 認証情報ファイルにproject_idが見つかりません。")
        except FileNotFoundError:
            raise ValueError(f"Credentials file not found: {credentials_path}. 認証情報ファイルが見つかりません: {credentials_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in credentials file: {credentials_path}. 認証情報ファイルのJSONが無効です: {credentials_path}")
        except Exception as e:
            raise ValueError(f"Error reading credentials file: {e}. 認証情報ファイルの読み込みエラー: {e}")
        
        self.client = translate.TranslationServiceClient()

        self.parent = f"projects/{self.project_id}/locations/global"
        self.from_language = from_language
        self.target_language = target_language
        self.max_translations = max_translations
        self.translation_count = 0

    def translate_text(self, text):
        if not text or not text.strip():
            return text

        # 最大翻訳回数を超えた場合は原文を返す
        if self.translation_count >= self.max_translations:
            return text

        request = {
            "parent": self.parent,
            "contents": [text],
            "mime_type": "text/plain",
            "target_language_code": self.target_language,
        }
        if self.from_language != 'auto':
            request["source_language_code"] = self.from_language

        try:
            response = self.client.translate_text(request=request)
            self.translation_count += 1
            return response.translations[0].translated_text
        except Exception as e:
            print(f"Translation API error: {e}")
            return text
