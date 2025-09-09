"""
mltpy.editor - Main class for MLT file editing / MLTファイル編集のメインクラス

Classes for loading, editing, and saving MLT files / MLTファイルの読み込み、編集、保存を行うクラス群
"""

from pathlib import Path
from lxml import etree
import re
from typing import Optional, Dict, Tuple, Union

from .subtitle_utils import SubtitleUtils
from .exceptions import (
    MLTFileNotFoundError,
    MLTParseError,
    MLTPlaylistNotFoundError,
    MLTOutputPathError,
)


class MLTEditor:
    """Main class for editing MLT files / MLTファイルの編集を行うメインクラス"""
    
    def __init__(self, input_path: Union[str, Path], playlist_id: int = 0):
        """
        Initialize MLT editor / MLTエディタを初期化
        
        Args:
            input_path: Path to the MLT file to edit / 編集対象のMLTファイルパス
            playlist_id: ID of the playlist to add subtitles / 字幕を追加するプレイリストのID
            
        Raises:
            MLTFileNotFoundError: When MLT file is not found / MLTファイルが見つからない場合
            MLTParseError: When parsing of MLT file fails / MLTファイルの解析に失敗した場合
            MLTPlaylistNotFoundError: When the specified playlist is not found / 指定したプレイリストが見つからない場合
        """
        self.input_path = Path(input_path)
        self.playlist_id = playlist_id
        self.playlist_id_str = f"playlist{playlist_id}"
        
        # Internal state / 内部状態
        self.tree = None
        self.mlt_tag = None
        self.playlist_elem = None
        self.output_path = None
        self.producer_id_counter = 0
        
        # Load MLT file at initialization / 初期化時にMLTファイルを読み込み
        self._load_mlt()
    
    def _load_mlt(self):
        """Load MLT file and initialize internal state / MLTファイルを読み込み、内部状態を初期化"""
        if not self.input_path.exists():
            raise MLTFileNotFoundError(self.input_path)
        
        try:
            # Load XML / XML を読み込む
            parser = etree.XMLParser(remove_blank_text=True)
            self.tree = etree.parse(self.input_path, parser)
            self.mlt_tag = self.tree.getroot()
        except etree.XMLSyntaxError as e:
            raise MLTParseError(self.input_path, str(e)) from e
        except Exception as e:
            raise MLTParseError(self.input_path, f"Unexpected error: {str(e)} / 予期しないエラー: {str(e)}") from e
        
        # Get playlist element / プレイリスト要素を取得
        self.playlist_elem = self.mlt_tag.find(f".//playlist[@id='{self.playlist_id_str}']")
        if self.playlist_elem is None:
            raise MLTPlaylistNotFoundError(self.playlist_id)
        
        # Initialize producer ID counter / プロデューサーIDカウンターを初期化
        max_producer_id = self._get_max_id('producer')
        self.producer_id_counter = max_producer_id + 1
    
    def set_output_path(self, suffix: str = "edited") -> Path:
        """
        Set output path / 出力パスを設定
        
        Args:
            suffix: Suffix to add to the filename / ファイル名に追加するサフィックス
            
        Returns:
            Configured output path / 設定された出力パス
            
        Raises:
            MLTOutputPathError: If there is a problem with the output path / 出力パスに問題がある場合
        """
        self.output_path = self.input_path.with_stem(f"{self.input_path.stem}_{suffix}")
        
        if self.input_path == self.output_path:
            raise MLTOutputPathError("Input path and output path are the same / 入力パスと出力パスが同じです")
        
        if self.output_path.exists():
            raise MLTOutputPathError(f"Output file already exists: {self.output_path} / 出力ファイルが既に存在します: {self.output_path}", self.output_path)
        
        return self.output_path
    
    @property
    def project_size(self) -> Tuple[int, int]:
        """Return project resolution as (width, height) tuple / プロジェクト解像度を (width, height) タプルで返す"""
        profile = self.mlt_tag.find("profile")
        if profile is None:
            raise MLTParseError(self.input_path, "No <profile> tag found in MLT file / MLTファイルに<profile>タグが見つかりません")
        
        try:
            width = int(profile.get("width"))
            height = int(profile.get("height"))
            return width, height
        except (TypeError, ValueError) as e:
            raise MLTParseError(self.input_path, f"Invalid project resolution: {str(e)} / 無効なプロジェクト解像度: {str(e)}") from e
    
    def _get_max_id(self, tag_name: str) -> int:
        """Get the maximum ID of the specified tag / 指定タグのIDの最大値を取得"""
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
        """Internal method to add producer and entry / プロデューサーとエントリーを追加する内部メソッド"""
        # Create producer element / プロデューサー要素を作成
        producer_elem = etree.Element("producer", id=f"producer{self.producer_id_counter}")
        producer_elem.set("in", "00:00:00.000")
        producer_elem.set("out", duration)
        
        # Resource property / リソースプロパティ
        if mlt_service == "timewarp":
            resource_text = f"4:{file_path.as_posix()}"
        else:
            resource_text = file_path.as_posix()
        
        etree.SubElement(producer_elem, "property", name="resource").text = resource_text
        etree.SubElement(producer_elem, "property", name="mlt_service").text = mlt_service
        
        # Additional properties / 追加プロパティ
        if extra_properties:
            for name, value in extra_properties.items():
                etree.SubElement(producer_elem, "property", name=name).text = value
        
        # Add producer / プロデューサーを追加
        playlist_index = self.mlt_tag.index(self.playlist_elem)
        self.mlt_tag.insert(playlist_index, producer_elem)
        
        # Add entry / エントリーを追加
        self._add_playlist_entry(self.producer_id_counter, duration)
        
        self.producer_id_counter += 1
    
    def _add_playlist_entry(self, producer_id: int, duration: str, entry_in: str = "00:00:00.000"):
        """Add entry to playlist / プレイリストにエントリーを追加"""
        entry_elem = etree.SubElement(self.playlist_elem, "entry")
        entry_elem.set("producer", f"producer{producer_id}")
        entry_elem.set("in", entry_in)
        entry_elem.set("out", duration)
        return entry_elem
    
    def _create_text_producer(self, producer_id: int, filter_id_start: int, 
                            text_arg: str, resource: str = "#ffffff"):
        """Create text producer / テキストプロデューサーを作成"""
        # Create producer / producer作成
        producer_elem = etree.Element("producer", id=f"producer{producer_id}")
        producer_elem.set("in", "00:00:00.000")
        producer_elem.set("out", "00:01:00.000")
        
        # Producer property / producerのproperty
        etree.SubElement(producer_elem, "property", name="mlt_service").text = "color"
        etree.SubElement(producer_elem, "property", name="resource").text = resource
        
        filter_id = filter_id_start
        
        # Affine filter / affineフィルター
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
        
        # Dynamictext filter / dynamictextフィルター
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
    
    def save(self, output_path: Optional[Union[str, Path]] = None):
        """
        Save MLT file / MLTファイルを保存
        
        Args:
            output_path: Path to save (if omitted, use internal output_path) / 保存先パス（省略時は内部のoutput_pathを使用）
            
        Raises:
            MLTOutputPathError: If output path is not set / 出力パスが設定されていない場合
        """
        if output_path:
            save_path = Path(output_path)
        elif self.output_path:
            save_path = self.output_path
        else:
            save_path = self.set_output_path()
        
        try:
            self.tree.write(save_path, encoding="utf-8", pretty_print=True, xml_declaration=True)
            print(f"MLT file saved at {save_path} / MLTファイルが {save_path} に保存されました。")
        except Exception as e:
            raise MLTOutputPathError(f"File save failed: {str(e)} / ファイル保存に失敗しました: {str(e)}", save_path) from e

    def extract_srt_data(self) -> Dict[str, str]:
        """
        Extract SRT subtitle data from MLT file (get all subtitle data) / MLTファイルからSRT字幕データを抽出（全ての字幕データを取得）
        
        Returns:
            Dictionary with filter ID as key and SRT string as value / filter IDをキーとし、SRT形式の字幕データ文字列を値とする辞書
            Empty dict if none found / 見つからない場合は空の辞書
        """
        srt_data_dict = {}
        
        # Search filter element with subtitle_feed service / subtitle_feedサービスを持つfilter要素を検索
        for filter_elem in self.mlt_tag.findall(".//filter"):
            # Get mlt_service property / mlt_serviceプロパティを取得
            service_elem = filter_elem.find("./property[@name='mlt_service']")
            if service_elem is not None and service_elem.text == "subtitle_feed":
                # Get text property within same filter / 同じfilter内のtextプロパティを取得
                text_elem = filter_elem.find("./property[@name='text']")
                if text_elem is not None and text_elem.text:
                    # Get filter ID / filter IDを取得
                    filter_id = filter_elem.get('id')
                    if filter_id:
                        # Decode HTML entities (&gt; → >) / HTMLエンティティをデコード（&gt; → >）
                        srt_text = text_elem.text.replace('&gt;', '>')
                        srt_data_dict[filter_id] = srt_text
        
        if not srt_data_dict:
            print("No subtitle data found. / 字幕データが見つかりませんでした。")
        else:
            print(f"{len(srt_data_dict)} subtitle data entries found. / {len(srt_data_dict)}個の字幕データが見つかりました。")
        
        return srt_data_dict

    def wrap_srt_lines(self, max_length: int = 90):
        """
        Wrap long lines of SRT subtitles in MLT file at specified length / MLTファイル内のSRT字幕データの長い行を指定文字数で改行
        
        Args:
            max_length: Max characters per line (default 90) / 1行の最大文字数（デフォルト90文字）
        """
        srt_dict = self.extract_srt_data()
        if not srt_dict:
            print("No subtitle data found, wrapping skipped. / 字幕データが見つからないため、改行処理は行われません。")
            return
        
        wrapped_dict = SubtitleUtils.wrap_srt_lines(srt_dict, max_length)

        self.update_srt_data(wrapped_dict)
        print(f"{len(wrapped_dict)} subtitle data entries wrapped. / {len(wrapped_dict)}個の字幕データが改行処理されました。")

    def update_srt_data(self, srt_dict: Dict[str, str]):
        """
        Update SRT subtitle data in MLT file / MLTファイル内のSRT字幕データを更新
        
        Args:
            srt_dict: Dict of updated SRT data keyed by filter ID / filter IDをキーとする更新後のSRTデータ辞書
        """
        updated_count = 0
        
        # Search filter element with subtitle_feed service / subtitle_feedサービスを持つfilter要素を検索
        for filter_elem in self.mlt_tag.findall(".//filter"):
            # Get mlt_service property / mlt_serviceプロパティを取得
            service_elem = filter_elem.find("./property[@name='mlt_service']")
            if service_elem is not None and service_elem.text == "subtitle_feed":
                filter_id = filter_elem.get('id')
                
                # If corresponding SRT data exists, update / 対応するSRTデータがある場合は更新
                if filter_id and filter_id in srt_dict:
                    text_elem = filter_elem.find("./property[@name='text']")
                    if text_elem is not None:
                        # Encode HTML entities (> → &gt;) / HTMLエンティティをエンコード（> → &gt;）
                        encoded_text = srt_dict[filter_id].replace('>', '&gt;')
                        text_elem.text = encoded_text
                        updated_count += 1
        
        print(f"{updated_count} subtitle data entries updated. / {updated_count}個の字幕データが更新されました。")

    def save_srt_file(self, srt_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Path]]:
        """
        Save extracted SRT subtitle data to file / 抽出したSRT字幕データをファイルに保存
        
        Args:
            srt_path: Directory path to save (if omitted, same as input file) / 保存先ディレクトリパス（省略時は入力ファイルと同じディレクトリ）
            
        Returns:
            Dict with filter ID as key and saved SRT path as value / filter IDをキーとし、保存されたSRTファイルのパスを値とする辞書
            None if no subtitle data found / 字幕データが見つからない場合はNone
            
        Raises:
            MLTOutputPathError: If file save fails / ファイル保存に失敗した場合
        """
        srt_data_dict = self.extract_srt_data()
        if not srt_data_dict:
            return None
        
        saved_files = {}
        
        if srt_path:
            save_dir = Path(srt_path)
            if save_dir.is_file():
                save_dir = save_dir.parent
        else:
            save_dir = self.input_path.parent
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        for filter_id, srt_data in srt_data_dict.items():
            # Generate filename (originalFileName_filterID.srt) / ファイル名を生成（元ファイル名_filterID.srt）
            filename = f"{self.input_path.stem}_{filter_id}.srt"
            save_path = save_dir / filename
            
            try:
                save_path.write_text(srt_data, encoding='utf-8')
                saved_files[filter_id] = save_path
                print(f"SRT file saved at {save_path} / SRTファイルが {save_path} に保存されました。")
            except Exception as e:
                raise MLTOutputPathError(f"SRT file save failed: {str(e)} / SRTファイル保存に失敗しました: {str(e)}", save_path) from e
        
        return saved_files
