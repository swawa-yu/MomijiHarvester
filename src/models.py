
from pydantic import AliasChoices, BaseModel, Field


class Subject(BaseModel):
    """
    Pydantic model representing a syllabus subject. Field aliases are set to
    Japanese headers used in the Momiji syllabus HTML tables so that parsed
    dictionaries with headers as keys can be passed directly to the model.
    """

    # 基本情報
    year: str | None = Field(None, alias="年度")
    faculty: str | None = Field(None, alias="開講部局")
    lecture_code: str | None = Field(None, alias="講義コード")
    category: str | None = Field(None, alias="科目区分")
    subject_name: str | None = Field(None, alias="授業科目名")
    subject_name_kana: str | None = Field(
        None,
        alias="授業科目名（フリガナ）",
        validation_alias=AliasChoices("授業科目名（フリガナ）", "授業科目名 （フリガナ）"),
    )
    english_subject_name: str | None = Field(None, alias="英文授業科目名")
    instructor_name: str | None = Field(None, alias="担当教員名")
    instructor_name_kana: str | None = Field(
        None,
        alias="担当教員名(フリガナ)",
        validation_alias=AliasChoices("担当教員名(フリガナ)", "担当教員名 (フリガナ)"),
    )
    campus: str | None = Field(None, alias="開講キャンパス")
    term: str | None = Field(None, alias="開設期")
    day_time_room: str | None = Field(None, alias="曜日・時限・講義室")

    # 授業の方法関連
    lecture_type: str | None = Field(None, alias="授業の方法")
    lecture_type_detail_1: str | None = Field(
        None,
        alias="授業の方法【詳細情報】",
        validation_alias=AliasChoices(
            "授業の方法【詳細情報】",
            "授業の方法 <BR> 【詳細情報】",
            "授業の方法<BR> 【詳細情報】",
        ),
    )

    # 時間・単位
    credits: str | None = Field(None, alias="単位")
    weekly_hours: str | None = Field(None, alias="週時間")
    language: str | None = Field(None, alias="使用言語")

    # 分野/対象
    learning_stage: str | None = Field(None, alias="学習の段階")
    discipline_field: str | None = Field(None, alias="学問分野（分野）")
    discipline_subfield: str | None = Field(None, alias="学問分野（分科）")
    target_students: str | None = Field(None, alias="対象学生")

    # メタ情報
    keywords: list[str] | None = Field(None, alias="授業のキーワード")
    teacher_professional: str | None = Field(None, alias="教職専門科目")
    subject_professional: str | None = Field(None, alias="教科専門科目")
    liberal_education_position: str | None = Field(
        None,
        alias="教養教育でのこの授業の位置づけ",
        validation_alias=AliasChoices("教養教育でのこの授業の位置づけ", "教養教育での\n この授業の位置づけ"),
    )

    # 文章長めのフィールド
    learning_outcomes: str | None = Field(None, alias="学習の成果")
    overview: str | None = Field(None, alias="授業の目標・概要等")
    plan: str | None = Field(None, alias="授業計画")
    textbooks: str | None = Field(None, alias="教科書・参考書等")

    # メディア・機器
    media_equipment: list[str] | None = Field(
        None,
        alias="授業で使用するメディア・機器等",
        validation_alias=AliasChoices("授業で使用するメディア・機器等", "授業で使用する メディア・機器等"),
    )
    media_equipment_detail: str | None = Field(None, alias="【詳細情報】")

    # 学習手法/アドバイス
    learning_methods: list[str] | None = Field(None, alias="授業で取り入れる学習手法")
    advice: str | None = Field(None, alias="予習・復習へのアドバイス")
    enrollment_notes: str | None = Field(
        None,
        alias="履修上の注意受講条件等",
        validation_alias=AliasChoices("履修上の注意受講条件等", "履修上の注意<BR> 受講条件等"),
    )
    grading: str | None = Field(None, alias="成績評価の基準等")

    # 実務経験/その他
    practical_experience: str | None = Field(None, alias="実務経験")
    practical_experience_detail: str | None = Field(None, alias="実務経験の概要とそれに基づく授業内容")
    message: str | None = Field(None, alias="メッセージ")
    other: str | None = Field(None, alias="その他")

    # Pydantic v2 configuration
    model_config = {
        "populate_by_name": True,
    }


# End of models.py

# from typing import TypedDict


# class Subject(TypedDict):
#     """
#     授業科目の情報を表すデータモデル
#     """


#     # "年度": str
#     # "開講部局": str
#     # "講義コード": str
#     # "科目区分": str
#     # "授業科目名": str
#     # "授業科目名 （フリガナ）": str  # 半角スペース注意
#     # "英文授業科目名": str
#     # "担当教員名": str
#     # "担当教員名 (フリガナ)": str  # 半角スペース注意
#     # "開講キャンパス": str
#     # "開設期": str
#     # "曜日・時限・講義室": str
#     # "授業の方法": str
#     # "授業の方法 【詳細情報】": str  # AliasChoices の Primary を採用
#     # "単位": str
#     # "週時間": str
#     # "使用言語": str
#     # "学習の段階": str
#     # "学問分野（分野）": str
#     # "学問分野（分科）": str
#     # "対象学生": str
#     # "授業のキーワード": str
#     # "教職専門科目": str
#     # "教科専門科目": str
#     # "教養教育での この授業の位置づけ": str  # AliasChoices の Primary を採用
#     # "学習の成果": str
#     # "授業の目標・概要等": str
#     # "授業計画": str
#     # "教科書・参考書等": str
#     # "授業で使用する メディア・機器等": str  # AliasChoices の Primary を採用
#     # "【詳細情報】": str,  # "授業で使用する..." の詳細
#     # "授業で取り入れる 学習手法": str,  # AliasChoices の Primary を採用
#     # "予習・復習への アドバイス": str,  # AliasChoices の Primary を採用
#     # "履修上の注意 受講条件等": str,  # AliasChoices の Primary を採用
#     # "成績評価の基準等": str,
#     # "実務経験": str,
#     # "実務経験の概要と それに基づく授業内容": str,  # AliasChoices の Primary を採用
#     # "メッセージ": str,
#     # "その他": str,
#     # # 注意: 最後の「授業改善アンケート」に関するヘッダーは意図的に除外（旧コード参考）



# class HeaderMismatchError(ValueError):
#     """ヘッダーがCanonical Headersと一致しない場合に送出される例外"""

#     pass
