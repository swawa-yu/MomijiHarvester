import json

import pandas as pd


class DataConverter:
    """
    抽出したシラバスデータをCSVおよびJSON形式に変換するクラス。
    """

    def to_csv(self, data, output_path):
        """
        データをCSV形式で出力します。
        data: リスト形式のデータ (各要素が辞書またはリスト)
        output_path: 出力するCSVファイルのパス
        """
        print(f"- CSVファイルを生成中: {output_path}...", end="")
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding="utf-8")
        print("完了")

    def csv_to_json(self, csv_file_path, json_file_path, drop_columns=[]):
        """
        シラバスの情報が含まれるCSVからJSONを生成します。

        csv_file_path: 入力CSVファイルのパス
        json_file_path: 出力JSONファイルのパス
        drop_columns: JSONに変換する際に削除する列名のリスト
        """
        print(f"- CSVからJSONを生成中: {json_file_path}...", end="")
        df = pd.read_csv(csv_file_path, dtype=str, keep_default_na=False)
        df = df.drop(columns=drop_columns, errors="ignore")  # errors='ignore'で存在しない列を指定してもエラーにならないようにする
        df = df.set_index("講義コード", drop=False)  # 講義コードをキーとする
        d = df.T.to_dict()

        with open(json_file_path, mode="w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)

        print("完了")


if __name__ == "__main__":
    # テスト用のコード (必要に応じて修正)
    # converter = DataConverter()
    #
    # # CSV出力テスト
    # sample_data = [
    #     {"Header1": "Data1_1", "Header2": "Data1_2"},
    #     {"Header1": "Data2_1", "Header2": "Data2_2"},
    # ]
    # converter.to_csv(sample_data, "test_output.csv")
    #
    # # CSV to JSON変換テスト
    # # test_output.csv が存在することを前提
    # converter.csv_to_json("test_output.csv", "test_output.json")
    pass
