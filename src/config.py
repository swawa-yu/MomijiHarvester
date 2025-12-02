# src/momijiharvester/config.py
import logging
from pathlib import Path

# --- 定数 ---
BASE_URL = "https://momiji.hiroshima-u.ac.jp/syllabusHtml/"
# ローカルHTMLファイルの場所(ディレクトリ構成変更後のパス)
LOCAL_HTML_DIR_FULL = Path("./tests/fixtures/html/full")
LOCAL_HTML_DIR_SMALL = Path("./tests/fixtures/html/small")
OUTPUT_DIR = Path("./output")

# --- Canonical Headers ---
# models.py の Subject モデルの alias (primary) を基準にする
# 順番も重要なのでリストで定義
CANONICAL_HEADERS = [
    "年度",
    "開講部局",
    "講義コード",
    "科目区分",
    "授業科目名",
    "授業科目名（フリガナ）",
    "英文授業科目名",
    "担当教員名",
    "担当教員名(フリガナ)",
    "開講キャンパス",
    "開設期",
    "曜日・時限・講義室",
    "授業の方法",
    "授業の方法【詳細情報】",
    "単位",
    "週時間",
    "使用言語",
    "学習の段階",
    "学問分野（分野）",
    "学問分野（分科）",
    "対象学生",
    "授業のキーワード",
    "教職専門科目",
    "教科専門科目",
    "教養教育でのこの授業の位置づけ",
    "学習の成果",
    "授業の目標・概要等",
    "授業計画",
    "教科書・参考書等",
    "授業で使用するメディア・機器等",
    "【詳細情報】",
    "授業で取り入れる学習手法",
    "予習・復習へのアドバイス",
    "履修上の注意受講条件等",
    "成績評価の基準等",
    "実務経験",
    "実務経験の概要とそれに基づく授業内容",
    "メッセージ",
    "その他",
]

# --- Logging ---
# --- 出力ディレクトリ作成 ---
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(OUTPUT_DIR / "momijiharvester.log", encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
