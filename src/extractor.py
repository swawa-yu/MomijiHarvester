"""SyllabusExtractorクラス

広島大学のシラバスHTMLファイルから情報を抽出し、LectureDetailモデルを生成するクラス。
"""

import copy
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from models import Department, LectureDetail


class SyllabusExtractor:
    """シラバスHTMLから情報を抽出し、データモデルを生成するクラス。"""

    def __init__(self, html_content: str) -> None:
        """コンストラクタ

        Args:
            html_content (str): 解析対象のHTML文字列
        """
        self.soup = BeautifulSoup(html_content, "html.parser")

    def extract_departments(self) -> List[Department]:
        """開講部局のリストを抽出する

        Returns:
            List[Department]: 開講部局情報リスト

        Raises:
            ValueError: 必要なリンク要素が見つからない場合
        """
        departments: List[Department] = []
        for link in self.soup.find_all("a"):
            if not isinstance(link, Tag):
                continue
            name = link.text.strip()
            if not name or name == "English":
                continue
            href_raw = link.get("href")
            href = str(href_raw) if href_raw else ""
            if not href.endswith(".html"):
                continue
            code = href[:-5]
            if code == "index":
                continue
            departments.append(Department(name=name, code=code, url=href))
        if not departments:
            raise ValueError("開講部局リンクが見つかりません")
        return departments

    def extract_lecture_detail(self) -> LectureDetail:
        """講義詳細ページから情報を抽出し、LectureDetailモデルを生成する

        Returns:
            LectureDetail: 講義詳細情報モデル

        Raises:
            ValueError: テーブルの構造が想定と異なる場合
        """
        soup = copy.deepcopy(self.soup)
        # <br>タグを改行へ置換
        for br in soup.find_all("br"):
            br.replace_with(NavigableString("\n"))

        # ヘッダーとデータ抽出
        heads = [" ".join(h.text.split()) for h in soup.find_all("th", class_="detail-head")]
        datas = [" ".join(d.get_text(separator="\n").split()).replace("\n", "\n") for d in soup.find_all("td", class_="detail-data")]

        # 不要な行を削除（14番目と末尾）
        if len(datas) >= 16:
            datas.pop(14)
            datas.pop()

        if len(heads) != len(datas):
            raise ValueError(f"ヘッダー数({len(heads)})とデータ数({len(datas)})が一致しません")

        # mapping to LectureDetail fields
        normalized: Dict[str, Any] = {}
        for key, val in zip(heads, datas):
            field = re.sub(r"[^\w\u4e00-\u9fff]+", "_", key).strip("_")
            normalized[field] = val or None

        try:
            return LectureDetail(**normalized)  # type: ignore
        except TypeError as e:
            raise ValueError(f"LectureDetailの初期化に失敗しました: {e}")
