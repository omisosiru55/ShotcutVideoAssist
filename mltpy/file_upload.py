from pathlib import Path
import requests

class FileUpload:
    @staticmethod
    def upload(file_path: str, server_url: str):
        """
        ファイルをストリームでアップロードする
        :param file_path: アップロードするファイルのパス
        :param server_url: Flaskサーバのアップロードエンドポイント
        """
        path = Path(file_path)
        headers = {
            "X-Filename": path.name
        }

        with path.open("rb") as f:
            response = requests.post(server_url, data=f, headers=headers, stream=True)

        if response.ok:
            print(f"Upload complete: {path.name}")
        else:
            print(f"Upload failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    FileUpload.upload(
        file_path="data.zip",
        server_url="http://192.168.0.3:5000/upload"
    )
