from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, Optional
import zipfile
import shutil
import requests
from .config import CLOUD_RENDER_BASE_URL
import xml.etree.ElementTree as ET


class MLTDataPackager:
    """
    MLT編集済みファイルをzip化し、アップロードするクラス。

    - 与えられた .mlt を解析し、全 producer/resource を data/<ファイル名> に書き換え
    - 修正版を {stem}_pathmod.mlt として保存
    - 上記とリソース群を data.zip に格納
    - data.zip を /upload エンドポイントにPOST
    """

    def __init__(self, mlt_path: Path | str):
        self.mlt_path: Path = Path(mlt_path).resolve()
        if not self.mlt_path.exists():
            raise FileNotFoundError(f"MLT file not found: {self.mlt_path}")

        self.work_dir: Path = self.mlt_path.parent
        self.modified_mlt_path: Path = self.work_dir / "cloud_rendering.mlt"
        self.zip_path: Path = self.work_dir / "data.zip"

        # 元パス -> zip内パス(data/xxx) の対応表
        self._path_mapping: Dict[Path, str] = {}

    def prepare_zip(self) -> Path:
        """
        data.zip を生成してパスを返す。
        既存の data.zip は削除する。
        """
        if self.zip_path.exists():
            try:
                self.zip_path.unlink()
            except Exception:
                # Windowsなどでロック発生時は上書き対策で一旦移動
                tmp = self.zip_path.with_suffix(".old.zip")
                try:
                    if tmp.exists():
                        tmp.unlink()
                    shutil.move(str(self.zip_path), str(tmp))
                except Exception:
                    pass

        tree, root = self._parse_mlt()

        # 全 producer / chain の resource を data/<basename> に書き換え
        self._path_mapping.clear()
        used_names: set[str] = set()

        def rewrite_resources_on_elements(elements):
            for elem in elements:
                for prop in elem.findall("property"):
                    if prop.get("name") == "resource" and prop.text:
                        original_text = prop.text.strip()
                        src_path = self._resolve_resource_path(original_text)
                        if src_path is None:
                            # ファイルパスでなければスキップ
                            continue
                        if not src_path.exists():
                            raise FileNotFoundError(f"Resource file not found: {src_path}")

                        arcname = self._allocate_arcname(src_path.name, used_names)
                        self._path_mapping[src_path] = f"data/{arcname}"
                        prop.text = f"data/{arcname}"

        # producerとchainを対象に実行
        rewrite_resources_on_elements(root.findall("producer"))
        rewrite_resources_on_elements(root.findall("chain"))

        # 修正版MLTを書き出し
        tree.write(self.modified_mlt_path, encoding="utf-8", xml_declaration=True)

        # ZIP作成
        with zipfile.ZipFile(self.zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # リソースを追加
            for src, arc in self._path_mapping.items():
                zf.write(src, arcname=arc)
            # 修正版MLTを追加（ルート直下にファイル名で）
            zf.write(self.modified_mlt_path, arcname=self.modified_mlt_path.name)

        return self.zip_path

    def upload(self, url: str | None = None, timeout: int = 60, progress_callback=None) -> Tuple[int, str]:
        """生成済み ZIP を指定URLへPOSTする。戻り値は (status_code, text)。"""
        if not self.zip_path.exists():
            raise FileNotFoundError("data.zip is not prepared. Call prepare_zip() first.")

        if url is None:
            url = f"{CLOUD_RENDER_BASE_URL}/upload"
        print(f"Uploading to {url}")
        headers = {
            "X-Filename": self.zip_path.name,
            "Content-Type": "application/octet-stream",
        }
        
        # ファイルサイズを取得
        file_size = self.zip_path.stat().st_size
        
        with self.zip_path.open("rb") as f:
            # アップロード進捗を追跡するためのカスタムアダプター
            class ProgressAdapter:
                def __init__(self, file_obj, callback, total_size):
                    self.file_obj = file_obj
                    self.callback = callback
                    self.total_size = total_size
                    self.uploaded = 0
                
                def read(self, size=-1):
                    data = self.file_obj.read(size)
                    if data and self.callback:
                        self.uploaded += len(data)
                        progress = (self.uploaded / self.total_size) * 100
                        self.callback(progress, self.uploaded, self.total_size)
                    return data
                
                def __getattr__(self, name):
                    return getattr(self.file_obj, name)
            
            progress_file = ProgressAdapter(f, progress_callback, file_size)
            resp = requests.post(url, data=progress_file, headers=headers, timeout=timeout)
        return resp.status_code, resp.text

    # ----------------------- 内部ユーティリティ -----------------------
    def _parse_mlt(self) -> Tuple[ET.ElementTree, ET.Element]:
        try:
            tree = ET.parse(self.mlt_path)
            return tree, tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse MLT XML: {e}")

    def _resolve_resource_path(self, value: str) -> Optional[Path]:
        """resource値がファイルパスであれば絶対Pathを返し、そうでなければNone。"""
        text = value.strip().strip('"')
        # 変数やURLスキームは除外
        if "://" in text:
            return None
        # 絶対パス or 相対パス
        p = Path(text)
        if not p.is_absolute():
            p = (self.work_dir / p).resolve()
        # 拡張子や区切りを基にファイルらしさを判定（存在確認は呼び出し側）
        if any(sep in text for sep in ("/", "\\")) or p.suffix:
            return p
        return None

    def _allocate_arcname(self, basename: str, used_names: set[str]) -> str:
        """ZIP内の衝突を避けるためのファイル名割り当て。"""
        name = basename
        stem = Path(basename).stem
        suffix = Path(basename).suffix
        idx = 1
        while name in used_names:
            name = f"{stem}_{idx}{suffix}"
            idx += 1
        used_names.add(name)
        return name


