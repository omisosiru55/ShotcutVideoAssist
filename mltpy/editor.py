"""
mltpy.editor - MLTファイル編集のメインクラス

MLTファイルの読み込み、編集、保存を行うクラス群
"""

from pathlib import Path
from lxml import etree
import re
from typing import Optional, Dict, Tuple, Union

from .media import MediaUtils
from .exceptions import (
    MLTFileNotFoundError,
    MLTParseError,
    MLTPlaylistNotFoundError,
    MLTOutputPathError,
    MediaFileNotFoundError,
    InvalidDurationError
)


class MLTEditor:
    """MLTファイルの編集を行うメインクラス"""
    
    def __init__(self, input_path: Union[str, Path], playlist_id: int = 4):
        """
        MLTエディタを初期化
        
        Args:
            input_path: 編集対象のMLTファイルパス
            playlist_id: 字幕を追加するプレイリストのID
            
        Raises:
            MLTFileNotFoundError: MLTファイルが見つからない場合
            MLTParseError: MLTファイルの解析に失敗した場合
            MLTPlaylistNotFoundError: 指定したプレイリストが見つからない場合
        """
        self.input_path = Path(input_path)
        self.playlist_id = playlist_id
        self.playlist_id_str = f"playlist{playlist_id}"
        
        # 内部状態
        self.tree = None
        self.mlt_tag = None
        self.playlist_elem = None
        self.output_path = None
        self.producer_id_counter = 0
        
        # 初期化時にMLTファイルを読み込み
        self._load_mlt()
    
    def _load_mlt(self):
        """MLTファイルを読み込み、内部状態を初期化"""
        if not self.input_path.exists():
            raise MLTFileNotFoundError(self.input_path)
        
        try:
            # XML を読み込む
            parser = etree.XMLParser(remove_blank_text=True)
            self.tree = etree.parse(self.input_path, parser)
            self.mlt_tag = self.tree.getroot()
        except etree.XMLSyntaxError as e:
            raise MLTParseError(self.input_path, str(e)) from e
        except Exception as e:
            raise MLTParseError(self.input_path, f"予期しないエラー: {str(e)}") from e
        
        # プレイリスト要素を取得
        self.playlist_elem = self.mlt_tag.find(f".//playlist[@id='{self.playlist_id_str}']")
        if self.playlist_elem is None:
            raise MLTPlaylistNotFoundError(self.playlist_id)
        
        # プロデューサーIDカウンターを初期化
        max_producer_id = self._get_max_id('producer')
        self.producer_id_counter = max_producer_id + 1
    
    def set_output_path(self, suffix: str = "edited") -> Path:
        """
        出力パスを設定
        
        Args:
            suffix: ファイル名に追加するサフィックス
            
        Returns:
            設定された出力パス
            
        Raises:
            MLTOutputPathError: 出力パスに問題がある場合
        """
        self.output_path = self.input_path.with_stem(f"{self.input_path.stem}_{suffix}")
        
        if self.input_path == self.output_path:
            raise MLTOutputPathError("入力パスと出力パスが同じです")
        
        if self.output_path.exists():
            raise MLTOutputPathError(f"出力ファイルが既に存在します: {self.output_path}", self.output_path)
        
        return self.output_path
    
    @property
    def project_size(self) -> Tuple[int, int]:
        """プロジェクト解像度を (width, height) タプルで返す"""
        profile = self.mlt_tag.find("profile")
        if profile is None:
            raise MLTParseError(self.input_path, "MLTファイルに<profile>タグが見つかりません")
        
        try:
            width = int(profile.get("width"))
            height = int(profile.get("height"))
            return width, height
        except (TypeError, ValueError) as e:
            raise MLTParseError(self.input_path, f"無効なプロジェクト解像度: {str(e)}") from e
    
    def _get_max_id(self, tag_name: str) -> int:
        """指定タグのIDの最大値を取得"""
        max_id = -1
        pattern = re.compile(rf'{re.escape(tag_name)}(\d+)')
        
        for elem in self.mlt_tag.findall(f'.//{tag_name}'):
            elem_id = elem.get('id')
            if elem_id:
                match = pattern.match(elem_id)
                if match:
                    current_id = int(match.group(1))
                    if current_id > max_id:
                        max_id = current_id
        
        return max_id
    
    def _add_producer_with_entry(self, file_path: Path, duration: str, 
                               mlt_service: str, extra_properties: Optional[Dict[str, str]] = None):
        """プロデューサーとエントリーを追加する内部メソッド"""
        # プロデューサー要素を作成
        producer_elem = etree.Element("producer", id=f"producer{self.producer_id_counter}")
        producer_elem.set("in", "00:00:00.000")
        producer_elem.set("out", duration)
        
        # リソースプロパティ
        if mlt_service == "timewarp":
            resource_text = f"4:{file_path.as_posix()}"
        else:
            resource_text = file_path.as_posix()
        
        etree.SubElement(producer_elem, "property", name="resource").text = resource_text
        etree.SubElement(producer_elem, "property", name="mlt_service").text = mlt_service
        
        # 追加プロパティ
        if extra_properties:
            for name, value in extra_properties.items():
                etree.SubElement(producer_elem, "property", name=name).text = value
        
        # プロデューサーを追加
        playlist_index = self.mlt_tag.index(self.playlist_elem)
        self.mlt_tag.insert(playlist_index, producer_elem)
        
        # エントリーを追加
        self._add_playlist_entry(self.producer_id_counter, duration)
        
        self.producer_id_counter += 1
    
    def _add_playlist_entry(self, producer_id: int, duration: str, entry_in: str = "00:00:00.000"):
        """プレイリストにエントリーを追加"""
        entry_elem = etree.SubElement(self.playlist_elem, "entry")
        entry_elem.set("producer", f"producer{producer_id}")
        entry_elem.set("in", entry_in)
        entry_elem.set("out", duration)
        return entry_elem
    
    def _create_text_producer(self, producer_id: int, filter_id_start: int, 
                            text_arg: str, resource: str = "#ffffff"):
        """テキストプロデューサーを作成"""
        # producer作成
        producer_elem = etree.Element("producer", id=f"producer{producer_id}")
        producer_elem.set("in", "00:00:00.000")
        producer_elem.set("out", "00:01:00.000")
        
        # producerのproperty
        etree.SubElement(producer_elem, "property", name="mlt_service").text = "color"
        etree.SubElement(producer_elem, "property", name="resource").text = resource
        
        filter_id = filter_id_start
        
        # affineフィルター
        filter1_elem = etree.SubElement(producer_elem, "filter", id=f"filter{filter_id}")
        filter1_elem.set("out", "00:01:00.000")
        
        filter1_props = {
            "background": "color:#00000000",
            "mlt_service": "affine",
            "shotcut:filter": "affineSizePosition",
            "transition.fill": "1",
            "transition.distort": "1",
            "transition.rect": "0 0 1920 70 1",
            "transition.valign": "top",
            "transition.halign": "center"
        }
        
        for name, value in filter1_props.items():
            etree.SubElement(filter1_elem, "property", name=name).text = value
        
        filter_id += 1
        
        # dynamictextフィルター
        filter2_elem = etree.SubElement(producer_elem, "filter", id=f"filter{filter_id}")
        filter2_elem.set("out", "00:01:00.000")
        
        filter2_props = {
            "argument": text_arg,
            "geometry": "2 0 1920 270 1",
            "family": "游明朝",
            "fgcolour": "#ff272727",
            "bgcolour": "#00000000",
            "halign": "left",
            "valign": "top",
            "mlt_service": "dynamictext",
            "shotcut:filter": "dynamicText",
            "shotcut:pointSize": "40",
            "shotcut:usePointSize": "1",
        }
        
        for name, value in filter2_props.items():
            etree.SubElement(filter2_elem, "property", name=name).text = value
        
        filter_id += 1
        
        return producer_elem, filter_id
    
    def get_producers_info(self) -> list:
        """現在のプロデューサー情報を取得"""
        producers = []
        for producer in self.mlt_tag.findall(".//producer"):
            producer_id = producer.get('id')
            resource_elem = producer.find(".//property[@name='resource']")
            mlt_service_elem = producer.find(".//property[@name='mlt_service']")
            
            info = {
                'id': producer_id,
                'resource': resource_elem.text if resource_elem is not None else None,
                'service': mlt_service_elem.text if mlt_service_elem is not None else None,
                'in': producer.get('in'),
                'out': producer.get('out')
            }
            producers.append(info)
        
        return producers
    
    def remove_producer(self, producer_id: str):
        """
        指定されたプロデューサーを削除
        
        Args:
            producer_id: 削除するプロデューサーのID
            
        Returns:
            削除された場合True、見つからない場合False
        """
        # プロデューサー要素を検索
        producer_elem = self.mlt_tag.find(f".//producer[@id='{producer_id}']")
        if producer_elem is not None:
            self.mlt_tag.remove(producer_elem)
            
            # 対応するエントリーも削除
            entry_elem = self.playlist_elem.find(f".//entry[@producer='{producer_id}']")
            if entry_elem is not None:
                self.playlist_elem.remove(entry_elem)
            
            return True
        
        return False
    
    def save(self, output_path: Optional[Union[str, Path]] = None):
        """
        MLTファイルを保存
        
        Args:
            output_path: 保存先パス（省略時は内部のoutput_pathを使用）
            
        Raises:
            MLTOutputPathError: 出力パスが設定されていない場合
        """
        if output_path:
            save_path = Path(output_path)
        elif self.output_path:
            save_path = self.output_path
        else:
            save_path = self.set_output_path()
        
        try:
            self.tree.write(save_path, encoding="utf-8", pretty_print=True, xml_declaration=True)
            print(f"MLTファイルが {save_path} に保存されました。")
        except Exception as e:
            raise MLTOutputPathError(f"ファイル保存に失敗しました: {str(e)}", save_path) from e
