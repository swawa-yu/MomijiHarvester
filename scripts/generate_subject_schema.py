from pathlib import Path
import json

from models import Subject


def generate_json_schema(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    schema = Subject.model_json_schema()
    # Post-process schema: make all properties non-nullable (i.e., remove 'null'
    # from anyOf constructs) and declare all properties required so the JSON
    # schema enforces string/integer-only values, with no null allowed.
    props = schema.get("properties", {})
    for k, v in props.items():
        # If anyOf is present and contains null and a type, simplify to that type.
        if "anyOf" in v and isinstance(v["anyOf"], list):
            types = [it for it in v["anyOf"] if isinstance(it, dict) and it.get("type") != "null"]
            if types:
                # If the simplified type is a dict with 'items', keep that structure
                schema_type = types[0]
                # Replace property with the schema_type (no null)
                props[k] = schema_type
    # Add required list with all property names (aliases) derived from the model
    try:
        from models import Subject as SubjectModel
        fields = SubjectModel.model_fields
        required_aliases = [getattr(f, "alias", name) for name, f in fields.items()]
        schema["required"] = required_aliases
    except Exception:
        pass
    json_path = out_dir / "subject.schema.json"
    json_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    return json_path, schema


def generate_markdown_schema(out_dir: Path, schema):
    md_path = out_dir / "SUBJECT_SCHEMA.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Subject JSON Schema\n\n")
        f.write("This document lists the `Subject` model field names, their JSON types, and a short description.\n\n")
        f.write("| field (alias) | JSON type | description |\n")
        f.write("|---|---|---:|---|\n")
        # Use the pydantic model fields when possible to preserve ordering
        try:
            from models import Subject as SubjectModel
            fields = SubjectModel.model_fields
        except Exception:
            fields = {}
        props = schema.get("properties", {})
        # `required` field is intentionally omitted from the markdown as all
        # fields are required; adding a column would be noisy.
        required_list = schema.get("required", [])
        for model_field_name, info in fields.items():
            # info is pydantic FieldInfo; fetch alias and annotation
            alias = getattr(info, "alias", model_field_name)
            json_spec = props.get(alias, {})
            json_type = json_spec.get("type", "")
            description = json_spec.get("title", "")
            if isinstance(description, str):
                description = description.replace("\n", " ")
            f.write(f"| `{alias}` | {json_type} | {description} |\n")
    return md_path


if __name__ == "__main__":
    out_dir = Path("schema")
    json_path, schema = generate_json_schema(out_dir)
    md_path = generate_markdown_schema(out_dir, schema)
    print("Generated:", json_path, md_path)
