from pathlib import Path
import json

from models import Subject


def generate_json_schema(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    schema = Subject.model_json_schema()
    json_path = out_dir / "subject.schema.json"
    json_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    return json_path, schema


def generate_markdown_schema(out_dir: Path, schema):
    md_path = out_dir / "SUBJECT_SCHEMA.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Subject JSON Schema\n\n")
        f.write("This document lists the `Subject` model field names, their types, and a short description.\n\n")
        f.write("| field (alias) | python type | JSON type | description |\n")
        f.write("|---|---|---:|---|\n")
        # Use the pydantic model fields when possible to preserve ordering
        try:
            from models import Subject as SubjectModel
            fields = SubjectModel.model_fields
        except Exception:
            fields = {}
        props = schema.get("properties", {})
        for model_field_name, info in fields.items():
            # info is pydantic FieldInfo; fetch alias and annotation
            alias = getattr(info, "alias", model_field_name)
            ann = getattr(info, "annotation", None)
            py_type = "any"
            if ann is not None:
                from typing import get_origin, get_args

                origin = get_origin(ann)
                if origin is list:
                    args = get_args(ann)
                    inner = "str"
                    if args:
                        inner = getattr(args[0], "__name__", str(args[0]))
                    py_type = f"list[{inner}]"
                else:
                    py_type = getattr(ann, "__name__", str(ann))

            json_spec = props.get(alias, {})
            json_type = json_spec.get("type", "")
            description = json_spec.get("title", "")
            if isinstance(description, str):
                description = description.replace("\n", " ")
            f.write(f"| `{alias}` | {py_type} | {json_type} | {description} |\n")
    return md_path


if __name__ == "__main__":
    out_dir = Path("schema")
    json_path, schema = generate_json_schema(out_dir)
    md_path = generate_markdown_schema(out_dir, schema)
    print("Generated:", json_path, md_path)
