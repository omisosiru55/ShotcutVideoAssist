from google.cloud import translate
import os
import requests
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
        if not os.getenv("GCLOUD_PROJECT_ID"):
            raise ValueError("Environment variable GCLOUD_PROJECT_ID is not set.\nPlease create a .env file and set GCLOUD_PROJECT_ID='your-project-id'. 環境変数 GCLOUD_PROJECT_ID が設定されていません。\n.env ファイルを作成してください。")
        
        self.client = translate.TranslationServiceClient()

        self.project_id = os.getenv("GCLOUD_PROJECT_ID")

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


class LibreTranslator:
    """
    LibreTranslate 用翻訳クラス
    """

    def __init__(self, from_language="auto", target_language="en", max_translations=1000, libre_url="https://libretranslate.com/translate"):
        """
        from_language: 翻訳元言語（'auto'で自動検出）
        target_language: 翻訳先言語
        max_translations: 最大翻訳回数。超えると原文を返す
        libre_url: LibreTranslateサーバのURL
        """
        self.from_language = from_language
        self.target_language = target_language
        self.max_translations = max_translations
        self.translation_count = 0
        self.libre_url = libre_url

    def translate_text(self, text):
        """
        text: 翻訳したい文字列
        """
        if not text or not text.strip():
            return text

        if self.translation_count >= self.max_translations:
            return text

        payload = {
            "q": text,
            "source": self.from_language,
            "target": self.target_language,
            "format": "text"
        }

        try:
            response = requests.post(self.libre_url, data=payload)
            response.raise_for_status()
            translated = response.json().get("translatedText", text)
            self.translation_count += 1
            return translated
        except Exception as e:
            print(f"LibreTranslate error: {e}")
            return text
