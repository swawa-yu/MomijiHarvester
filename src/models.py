"""MomijiHarvester データモデル定義

HTML から抽出したデータを格納するデータクラスを定義します。
"""

from dataclasses import dataclass
from typing import Optional


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

    年度: Optional[str] = None
    開講部局: Optional[str] = None
    講義コード: Optional[str] = None
    科目区分: Optional[str] = None
    授業科目名: Optional[str] = None
    授業科目名_フリガナ: Optional[str] = None
    英文授業科目名: Optional[str] = None
    担当教員名: Optional[str] = None
    担当教員名_フリガナ: Optional[str] = None
    開講キャンパス: Optional[str] = None
    開設期: Optional[str] = None
    曜日_時限_講義室: Optional[str] = None
    授業の方法: Optional[str] = None
    授業の方法_詳細情報: Optional[str] = None
    単位: Optional[str] = None
    週時間: Optional[str] = None
    使用言語: Optional[str] = None
    学習の段階: Optional[str] = None
    学問分野_分野: Optional[str] = None
    学問分野_分科: Optional[str] = None
    対象学生: Optional[str] = None
    授業のキーワード: Optional[str] = None
    教職専門科目: Optional[str] = None
    教科専門科目: Optional[str] = None
    教養教育での_この授業の位置づけ: Optional[str] = None
    学習の成果: Optional[str] = None
    授業の目標_概要等: Optional[str] = None
    授業計画: Optional[str] = None
    教科書_参考書等: Optional[str] = None
    授業で使用する: Optional[str] = None
    授業で使用する_メディア_機器等: Optional[str] = None
    詳細情報: Optional[str] = None
    授業で取り入れる_学習手法: Optional[str] = None
    予習_復習への_アドバイス: Optional[str] = None
    履修上の注意_受講条件等: Optional[str] = None
    成績評価の基準等: Optional[str] = None
    実務経験: Optional[str] = None
    実務経験の概要と_それに基づく授業内容: Optional[str] = None
    メッセージ: Optional[str] = None
    その他: Optional[str] = None
