from typing import Any, get_args, get_origin

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from pydantic import AliasChoices

import config
from models import Subject


class HeaderMismatchError(ValueError):
    """ヘッダーがCanonical Headersと一致しない場合に送出される例外"""

    pass


def extract_headers(soup: BeautifulSoup) -> list[str]:
    """HTMLスープからヘッダーテキストのリストを抽出する"""
    headers = []
    th_tags = soup.select("table > tbody > tr > th.detail-head")
    for th in th_tags:
        if isinstance(th, Tag):
            header_text = " ".join(th.get_text(strip=True).split())
            headers.append(header_text)
    return headers


def validate_headers(actual_headers: list[str], file_identifier: str = "Unknown HTML"):
    """
    抽出されたヘッダーとCanonicalヘッダーを比較検証する。
    不一致があればログを出力し、致命的な場合は例外を送出する。
    """
    canonical_set = set(config.CANONICAL_HEADERS)
    actual_set = set(actual_headers)
    unexpected_headers = actual_set - canonical_set
    missing_headers = canonical_set - actual_set
    error_occurred = False
    if unexpected_headers:
        config.logger.error(f"[{file_identifier}] Unexpected headers found: {unexpected_headers}")
        error_occurred = True
    if missing_headers:
        config.logger.warning(f"[{file_identifier}] Expected headers missing: {missing_headers}")
    if error_occurred:
        # Keep message length reasonable to satisfy linters by splitting into two logs
        raise HeaderMismatchError(
            f"Header mismatch detected in {file_identifier}. Unexpected: {unexpected_headers}"
        )
    else:
        config.logger.info(f"[{file_identifier}] Headers validated successfully.")


def _parse_detail_table(soup: BeautifulSoup) -> dict[str, str]:
    """
    シラバス詳細テーブルを解析し、ヘッダーとデータの辞書を作成する。
    rowspanを考慮する。
    """
    data_dict: dict[str, str] = {}
    table = soup.select_one("body > blockquote > table:nth-of-type(2)")
    if not table or not isinstance(table, Tag):
        config.logger.error("Detail table not found or is not a Tag in HTML.")
        return data_dict

    # Find all rows (allow tbody wrapper added by parser)
    rows = table.find_all("tr")
    row_span_offset: dict[int, tuple[int, str, str]] = {}

    for row in rows:
        if not isinstance(row, Tag):
            continue
        cells = row.find_all(["th", "td"], recursive=False)
        current_col_idx = 0
        header: str | None = None

        processed_indices = set()

        indices_to_process = sorted(row_span_offset.keys())
        for col_idx in indices_to_process:
            if col_idx >= current_col_idx:
                remaining_span, span_header, _ = row_span_offset[col_idx]
                if remaining_span == 1:
                    del row_span_offset[col_idx]
                else:
                    row_span_offset[col_idx] = (remaining_span - 1, span_header, _)
                processed_indices.add(col_idx)
                current_col_idx = col_idx + 1

        for cell in cells:
            if not isinstance(cell, Tag):
                continue

            while current_col_idx in processed_indices:
                current_col_idx += 1

            rowspan_str = cell.get("rowspan", "1")
            colspan_str = cell.get("colspan", "1")
            try:
                rowspan = int(str(rowspan_str)) if rowspan_str else 1
                colspan = int(str(colspan_str)) if colspan_str else 1
            except (ValueError, TypeError):
                config.logger.warning(
                    "Could not convert rowspan/colspan to int for cell %s: rowspan=%s colspan=%s (defaulting to 1).",
                    cell.name,
                    rowspan_str,
                    colspan_str,
                )
                rowspan = 1
                colspan = 1

            if cell.name == "th":
                header = " ".join(cell.get_text(strip=True).split())
            elif cell.name == "td" and header:
                for br in cell.find_all("br"):
                    try:
                        br.replace_with(NavigableString("\n"))
                    except NameError:
                        config.logger.error("NavigableString seems not imported correctly.")
                        br.replace_with(NavigableString("\n"))

                data = cell.get_text(separator=" ", strip=True)

                effective_header = header
                if rowspan > 1:
                    for i in range(colspan):
                        col_to_apply = current_col_idx + i
                        row_span_offset[col_to_apply] = (rowspan - 1, effective_header, data)
                        processed_indices.add(col_to_apply)

                if effective_header not in data_dict:
                    data_dict[effective_header] = data

            current_col_idx += colspan
    return data_dict


def _clean_value(value: str | None) -> str | None:
    """文字列の前後の空白、特殊文字（例: &nbsp;）を除去"""
    if value is None:
        return None
    # Replace non-breaking and ideographic spaces, normalize parentheses
    cleaned = value.replace("\xa0", " ")
    cleaned = cleaned.replace("\u3000", " ")
    cleaned = cleaned.replace("（", "(")
    cleaned = cleaned.replace("）", ")")
    # Collapse any whitespace sequences (including converted NBSP/IDEOGRAPHIC) down to a single space
    cleaned = " ".join(cleaned.split())
    return cleaned if cleaned else None


def _split_list_value(value: str | None) -> list[str] | None:
    """カンマ区切りの文字列をリストに分割"""
    if value is None:
        return None
    # split on comma, japanese comma, and common separators
    separators = [",", "、", "，", ";"]
    tmp = value.strip()
    for sep in separators:
        tmp = tmp.replace(sep, ",")
    items = [item.strip() for item in tmp.split(",") if item.strip()]
    return items if items else None


def extract_subject_data(html_content: str, file_identifier: str) -> Subject | None:
    """
    HTMLコンテンツ文字列から Subject モデルのデータを抽出する。
    ヘッダー検証を含む。
    """
    soup = BeautifulSoup(html_content, "html5lib")

    try:
        actual_headers = extract_headers(soup)
        validate_headers(actual_headers, file_identifier)
    except HeaderMismatchError as e:
        config.logger.error(f"Stopping extraction for {file_identifier} due to header mismatch: {e}")
        return None
    except Exception as e:
        config.logger.error(f"Error during header extraction/validation for {file_identifier}: {e}")
        return None

    try:
        raw_data_dict = _parse_detail_table(soup)
    except Exception as e:
        config.logger.error(f"Error parsing detail table for {file_identifier}: {e}")
        return None

    # If there are no parsed values, treat HTML as invalid and stop
    if not raw_data_dict:
        config.logger.warning(f"No detail data parsed for {file_identifier}; skipping subject extraction.")
        return None

    subject_data: dict[str, Any] = {}
    # Pylance のエラーを抑制 (型推論が難しいため)
    for field_name, field_info in Subject.model_fields.items():  # type: ignore
        primary_alias = field_info.alias
        possible_keys: set[str] = set()
        if primary_alias and isinstance(primary_alias, str):
            possible_keys.add(primary_alias)

        validation_alias = field_info.validation_alias
        if validation_alias and isinstance(validation_alias, AliasChoices):
            possible_keys.update(c for c in validation_alias.choices if isinstance(c, str))

        br_variants: set[str] = set()
        for key in possible_keys:
            if key and " " in key:
                br_variants.add(key.replace(" ", "<br>"))
                br_variants.add(key.replace(" ", "<BR>"))
                br_variants.add(key.replace(" ", "<br/>"))
                br_variants.add(key.replace(" ", "<BR/>"))
        possible_keys.update(br_variants)

        raw_value = None
        for key in possible_keys:
            if key in raw_data_dict:
                raw_value = raw_data_dict[key]
                break

        cleaned_value = _clean_value(raw_value)
        annotation_origin = get_origin(field_info.annotation)
        annotation_args = get_args(field_info.annotation)
        # Handle Optional[List[str]] and List[str] by checking Union/Optional
        is_list_type = False
        try:
            if annotation_origin is list:
                is_list_type = True
            elif getattr(field_info.annotation, "__origin__", None) is list:
                # typing.List[str] fallback
                is_list_type = True
            elif annotation_args:
                for arg in annotation_args:
                    if get_origin(arg) is list or getattr(arg, "__origin__", None) is list:
                        is_list_type = True
                        break
        except Exception:
            is_list_type = False

        if is_list_type:
            subject_data[field_name] = _split_list_value(cleaned_value)
        else:
            subject_data[field_name] = cleaned_value

    try:
        subject = Subject(**subject_data)
        return subject
    except Exception as e:
        config.logger.error(f"[{file_identifier}] Error creating/validating Subject model: {e}")
        config.logger.debug(f"Data used for validation: {subject_data}")
        return None
