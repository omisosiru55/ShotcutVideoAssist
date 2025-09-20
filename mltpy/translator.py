from google.cloud import translate
import os

class GoogleTranslator:
    def __init__(self, from_language="auto", target_language="en", max_translations=1000):
        """
        from_language: 翻訳元の言語（'auto'で自動検出）
        target_language: 翻訳先の言語
        max_translations: 最大翻訳回数。超えると原文を返す
        """
        self.client = translate.TranslationServiceClient()

        self.project_id = os.getenv("GCLOUD_PROJECT_ID")
        if not self.project_id:
            raise ValueError("環境変数 'GCLOUD_PROJECT_ID' が設定されていません。")

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
