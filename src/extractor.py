import copy
from bs4.element import Tag, NavigableString  # TagとNavigableStringをインポート

# 定数定義
MIN_DETAIL_DATA_COUNT = 15
INDEX_TO_POP_FIRST = 14


class SyllabusExtractor:
    """
    シラバスHTMLから授業情報を抽出するクラス。
    """

    def extract_subject_detail_data(self, bsoup):
        """
        授業情報が含まれるテーブルをbsoupとして受け取り、授業情報を抽出します。
        """
        # <br>タグを改行文字に置き換えるため、一旦__BR__という文字列に置き換える
        # 引数で受け取ったbsoupは書き換えられてしまうので、コピーを作成
        bsoup = copy.deepcopy(bsoup)
        for br in bsoup.find_all("br"):
            br.replace_with("__BR__")

        # detail-dataクラスを持つtdタグからデータを抽出
        detail_datas = []
        for d in bsoup.find_all("td", class_="detail-data"):
            # <br>タグを改行に置き換え、それ以外の連続する空白や改行は1つのスペースにまとめる
            text = ""
            for content in d.contents:
                if isinstance(content, NavigableString):
                    text += " ".join(str(content).split())  # 連続する空白や改行を1つのスペースにまとめ
                elif isinstance(content, Tag) and content.name == "br":
                    text += "\n"  # <br>タグを改行に変換
                elif isinstance(content, Tag):
                    text += " ".join(content.get_text().split())  # タグ内のテキストを取得し、空白をまとめる
            detail_datas.append(text.strip())  # 前後の空白を削除

        # 謎の空白と授業改善アンケートの説明の欄を削除
        # TODO: 削除するインデックスが固定になっているため、HTML構造の変更に弱い。
        # より堅牢な方法で必要なデータのみを抽出するように修正が必要。
        if len(detail_datas) > MIN_DETAIL_DATA_COUNT:  # 要素数が十分にあるか確認
            detail_datas.pop(INDEX_TO_POP_FIRST)
        if len(detail_datas) > 0:  # 要素数が十分にあるか確認
            detail_datas.pop()

        return detail_datas

    def get_subject_detail_head(self, bsoup):
        """
        授業情報が含まれるテーブルをbsoupとして受け取り、ヘッダーを抽出します。
        """
        detail_heads = [" ".join(h.text.split()) for h in bsoup.find_all("th", class_="detail-head")]
        return detail_heads


if __name__ == "__main__":
    # テスト用のコード (必要に応じて修正)
    # from pathlib import Path
    #
    # html_path = Path('../docs/syllabusHtml-small/2025_AA_10000100.html')
    # with open(html_path, 'r', encoding='utf-8') as f:
    #     html_content = f.read()
    #
    # soup = BeautifulSoup(html_content, 'html.parser')
    #
    # extractor = SyllabusExtractor()
    # heads = extractor.get_subject_detail_head(soup)
    # datas = extractor.extract_subject_detail_data(soup)
    #
    # print("Headers:", heads)
    # print("Data:", datas)
    pass
