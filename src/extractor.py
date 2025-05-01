"""SyllabusExtractorクラス

広島大学のシラバスHTMLファイルから情報を抽出するクラス。
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup


class SyllabusExtractor:
    """シラバスHTMLから情報を抽出するクラス。

    Attributes:
        html_content (str): 解析対象のHTML文字列
    """

    def __init__(self, html_content: str) -> None:
        """コンストラクタ

        Args:
            html_content (str): 解析対象のHTML文字列
        """
        self.html_content = html_content
        self.soup = BeautifulSoup(html_content, "html.parser")

    def extract_departments(self) -> List[Dict[str, Any]]:
        """開講部局のリストを抽出する

        Returns:
            List[Dict[str, Any]]: 開講部局情報のリスト
        """
        # TODO: 実装
        return []

    def extract_lectures(self) -> List[Dict[str, Any]]:
        """講義リンクのリストを抽出する

        Returns:
            List[Dict[str, Any]]: 講義情報のリスト
        """
        # TODO: 実装
        return []

    def extract_lecture_detail(self) -> Dict[str, Any]:
        """講義詳細ページから情報を抽出する

        Returns:
            Dict[str, Any]: 講義詳細情報
        """
        # TODO: 実装
        return {}
