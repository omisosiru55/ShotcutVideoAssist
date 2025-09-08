"""
mltpy.subtitle_utils - 字幕処理ユーティリティ

字幕データの変換、フォーマット、改行処理などを行うユーティリティクラス
"""

from typing import Dict, List
import re


class SubtitleUtils:
    """字幕データ処理のユーティリティクラス"""
    
    @staticmethod
    def wrap_srt_lines(srt_dict: Dict[str, str], max_length: int = 90) -> Dict[str, str]:
        """
        SRTデータの長い行を指定文字数で改行
        
        Args:
            srt_dict: filter IDをキーとするSRTデータの辞書
            max_length: 1行の最大文字数（デフォルト90文字）
            
        Returns:
            改行処理されたSRTデータの辞書
        """
        wrapped_dict = {}
        
        for filter_id, srt_data in srt_dict.items():
            lines = srt_data.split('\n')
            wrapped_lines = []
            
            for line in lines:
                # タイムコード行や番号行はそのまま保持
                if (line.strip().isdigit() or 
                    '-->' in line or 
                    line.strip() == ''):
                    wrapped_lines.append(line)
                else:
                    # 字幕テキスト行を改行処理
                    wrapped_text_lines = SubtitleUtils._wrap_text_line(line, max_length)
                    wrapped_lines.extend(wrapped_text_lines)
            
            wrapped_dict[filter_id] = '\n'.join(wrapped_lines)
        
        return wrapped_dict

    @staticmethod
    def _wrap_text_line(line: str, max_length: int) -> List[str]:
        """
        単一のテキスト行を改行処理
        
        Args:
            line: 処理対象の行
            max_length: 1行の最大文字数
            
        Returns:
            改行処理された行のリスト
        """
        if len(line) <= max_length:
            return [line]
        
        wrapped_lines = []
        current_line = ""
        words = line.split(' ')
        
        for word in words:
            # 単語自体が最大長を超える場合は強制分割
            if len(word) > max_length:
                if current_line:
                    wrapped_lines.append(current_line.strip())
                    current_line = ""
                # 長い単語を強制分割
                while len(word) > max_length:
                    wrapped_lines.append(word[:max_length])
                    word = word[max_length:]
                if word:
                    current_line = word + " "
            else:
                # 単語を追加すると最大長を超える場合
                if len(current_line) + len(word) + 1 > max_length:
                    if current_line:
                        wrapped_lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    current_line += word + " "
        
        # 残りの文字列を追加
        if current_line.strip():
            wrapped_lines.append(current_line.strip())
        
        return wrapped_lines