from typing import List, Dict
import pandas as pd
from exceptions import ValidationError

REQUIRED_COLUMNS = ["title", "notes_on_outline_before"]


def read_excel_rows(file_path: str) -> List[Dict]:
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError as exc:
        raise ValidationError(f"Excel file not found: {file_path}") from exc
    except Exception as exc:
        raise ValidationError(f"Could not read Excel file: {exc}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValidationError(f"Missing required columns: {', '.join(missing)}")

    records = df.fillna("").to_dict(orient="records")
    return records
