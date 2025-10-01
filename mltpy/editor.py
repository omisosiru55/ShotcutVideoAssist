"""
mltpy.editor - Main class for MLT file editing / MLTファイル編集のメインクラス

Classes for loading, editing, and saving MLT files / MLTファイルの読み込み、編集、保存を行うクラス群
"""

from pathlib import Path
from lxml import etree
import re
from typing import Optional, Dict, Tuple, Union
import zipfile
from translate import Translator

from .subtitle_utils import SubtitleUtils
from .translator import GoogleTranslator
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
        Args: suffix: Suffix to add to the filename / ファイル名に追加するサフィックス
        Returns: Configured output path / 設定された出力パス
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
    
    def save(self, output_path: Optional[Union[str, Path]] = None):
        """
        Save MLT file / MLTファイルを保存
        Args: output_path: Path to save (if omitted, use internal output_path) / 保存先パス（省略時は内部のoutput_pathを使用）
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

    def wrap_dynamictext_lines(self, max_length: int = 90, force_wrap: bool = False):

        self.set_output_path(f"dynwrapped{max_length}")

        wrapped_count = 0
        for producer in self.mlt_tag.findall("producer"):
            for filter_elem in producer.findall("filter"):
                if filter_elem.get("mlt_service") == "dynamictext" or filter_elem.find("property[@name='mlt_service']").text == "dynamictext":
                    for prop in filter_elem.findall("property[@name='argument']"):
                        original = prop.text
                        wrapped_text_lines = SubtitleUtils.wrap_text_line(original, max_length, force_wrap)
                        # Join wrapped lines with newline character
                        wrapped = '\n'.join(wrapped_text_lines)
                        prop.text = wrapped
                        wrapped_count += 1
                        print(f"Wrapped dynamictext: {original} -> {wrapped}")

        print(f"Total dynamictext filters wrapped: {wrapped_count} / 改行されたdynamictextフィルタの総数: {wrapped_count}")
        return wrapped_count

    # dynamictextを翻訳する / translate dynamictext
    def translate_dynamictext(self, from_lang: str = 'en', to_lang: str = 'fr', service: str = 'Libre') -> int:

        self.set_output_path(f"translated{from_lang}to{to_lang}")

        if service == 'Translate':
            translator = Translator(from_lang=from_lang, to_lang=to_lang)
        else:
            translator = GoogleTranslator(from_language=from_lang, target_language=to_lang)

        translated_count = 0
        for producer in self.mlt_tag.findall("producer"):
            for filter_elem in producer.findall("filter"):
                if filter_elem.get("mlt_service") == "dynamictext" or filter_elem.find("property[@name='mlt_service']").text == "dynamictext":
                    for prop in filter_elem.findall("property[@name='argument']"):
                        original = prop.text
                        if service == 'Translate':
                            translated = translator.translate(original)
                        else:
                            translated = translator.translate_text(original)
                        prop.text = translated
                        translated_count += 1
                        print(f"Translated dynamictext: {original} -> {translated}")

        print(f"Total dynamictext filters translated: {translated_count} / 翻訳されたdynamictextフィルタの総数: {translated_count}")
        return translated_count

    # 字幕関連のメソッド / Subtitle-related methods
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
                        #srt_text = text_elem.text.replace('&gt;', '>')
                        #srt_data_dict[filter_id] = srt_text
                        srt_data_dict[filter_id] = text_elem.text
        
        if not srt_data_dict:
            print("No subtitle data found. / 字幕データが見つかりませんでした。")
        else:
            print(f"{len(srt_data_dict)} subtitle data entries found. / {len(srt_data_dict)}個の字幕データが見つかりました。")
        
        return srt_data_dict

    def wrap_srt_lines(self, max_length: int = 90, force_wrap: bool = False):
        """
        Wrap long lines of SRT subtitles in MLT file at specified length / MLTファイル内のSRT字幕データの長い行を指定文字数で改行
        
        Args:
            max_length: Max characters per line (default 90) / 1行の最大文字数（デフォルト90文字）
            force_wrap: Force wrapping lines even without spaces, useful for languages like Chinese / スペースがない言語（中国語など）でも強制的に行を折り返す
        """
        self.set_output_path(f"sbtwrapped{max_length}")

        srt_dict = self.extract_srt_data()
        if not srt_dict:
            print("No subtitle data found, wrapping skipped. / 字幕データが見つからないため、改行処理は行われません。")
            return
        
        wrapped_dict = SubtitleUtils.wrap_srt_lines(srt_dict, max_length, force_wrap)

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
                        #encoded_text = srt_dict[filter_id].replace('>', '&gt;')
                        #text_elem.text = encoded_text
                        text_elem.text = srt_dict[filter_id]
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

    def modify_qtcrop_color(self) -> int:
        """
        qtcropフィルターのcolorプロパティで末尾が00（透明）の場合、
        最初の6桁をFFFFFF（白）に変更し、stemに_modqtcropを付けて保存する / 
        For qtcrop filter color properties ending with 00 (transparent), 
        change first 6 digits to FFFFFF (white) and save with _modqtcrop suffix
        
        Returns:
            int: 変更されたフィルターの数 / Number of modified filters
        """
        self.set_output_path("modqtcrop")
        
        modified_count = 0
        
        # qtcropサービスを持つフィルターを検索 / Search for filters with qtcrop service
        for filter_elem in self.mlt_tag.findall(".//filter"):
            # mlt_serviceプロパティを確認 / Check mlt_service property
            service_elem = filter_elem.find("./property[@name='mlt_service']")
            if service_elem is not None and service_elem.text == "qtcrop":
                # 同じフィルター内のcolorプロパティを検索 / Search for color property in same filter
                color_elem = filter_elem.find("./property[@name='color']")
                if color_elem is not None and color_elem.text and color_elem.text.endswith("00"):
                    # 最後の2桁が00（透明）の場合、最初の6桁をFFFFFF（白）に変更 / If last 2 digits are 00 (transparent), change first 6 digits to FFFFFF (white)
                    original_color = color_elem.text
                    color_elem.text = "#FFFFFFFF"
                    modified_count += 1
                    print(f"Modified qtcrop filter color: {filter_elem.get('id', 'unknown')} - {original_color} -> #FFFFFFFF")
        
        if modified_count == 0:
            print("No qtcrop filters with transparent color (ending with 00) found. / 透明色（末尾が00）を持つqtcropフィルターが見つかりませんでした。")
        else:
            print(f"Total qtcrop filters modified: {modified_count} / 変更されたqtcropフィルターの総数: {modified_count}")
        
        return modified_count

    # レンダリングサービス用メソッド群 / methods for rendering services
    def modify_resource_directory(self):
        # resource プロパティを全て探す
        for prop in self.mlt_tag.xpath(".//property[@name='resource']"):
            old_path = prop.text
            if not old_path:
                continue

            # 数値:で始まる場合（例：2:c:/path, 1.5:c:/path）は先頭の数値部分を削除
            match = re.match(r'^(\d+(?:\.\d)?):(.+)$', old_path)
            if match:
                old_path = match.group(2)  # 数値部分を除いた残りを取得

            filename = Path(old_path).name

            # data/xxx に置き換える
            new_path = Path("data") / filename
            prop.text = str(new_path)

            self.resources.append(Path(old_path))
        
        self.create_data_zip()

        self.set_output_path("renderready")

    def create_data_zip(self, zip_path="data.zip"):
        """収集したファイルを data.zip にまとめる"""
        zip_file = Path(zip_path)

        # 既存の data.zip があれば削除
        if zip_file.exists():
            zip_file.unlink()

        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in self.resources:
                if file.exists():
                    arcname = f"data/{file.name}"  # zip 内の保存パス
                    zf.write(file, arcname=arcname)
                else:
                    print(f"⚠️ ファイルが見つかりません: {file}")            