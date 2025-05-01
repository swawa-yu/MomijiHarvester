# ruff: noqa: PLC2401
"""MomijiHarvester データモデル定義

HTML から抽出したデータを格納するデータクラスを定義します。
"""

from dataclasses import dataclass


@dataclass
class Department:
    """開講部局情報を表すデータクラス."""

    name: str
    code: str
    url: str


@dataclass
class LectureDetail:
    """講義詳細情報を表すデータクラス.

    HTML の detail-head/ detail-data テーブルから抽出される各項目です。
    """

    年度: str | None = None
    開講部局: str | None = None
    講義コード: str | None = None
    科目区分: str | None = None
    授業科目名: str | None = None
    授業科目名_フリガナ: str | None = None
    英文授業科目名: str | None = None
    担当教員名: str | None = None
    担当教員名_フリガナ: str | None = None
    開講キャンパス: str | None = None
    開設期: str | None = None
    曜日_時限_講義室: str | None = None
    授業の方法: str | None = None
    授業の方法_詳細情報: str | None = None
    単位: str | None = None
    週時間: str | None = None
    使用言語: str | None = None
    学習の段階: str | None = None
    学問分野_分野: str | None = None
    学問分野_分科: str | None = None
    対象学生: str | None = None
    授業のキーワード: str | None = None
    教職専門科目: str | None = None
    教科専門科目: str | None = None
    教養教育での_この授業の位置づけ: str | None = None
    学習の成果: str | None = None
    授業の目標_概要等: str | None = None
    授業計画: str | None = None
    教科書_参考書等: str | None = None
    授業で使用する: str | None = None
    授業で使用する_メディア_機器等: str | None = None
    詳細情報: str | None = None
    授業で取り入れる_学習手法: str | None = None
    予習_復習への_アドバイス: str | None = None
    履修上の注意_受講条件等: str | None = None
    成績評価の基準等: str | None = None
    実務経験: str | None = None
    実務経験の概要と_それに基づく授業内容: str | None = None
    メッセージ: str | None = None
    その他: str | None = None
