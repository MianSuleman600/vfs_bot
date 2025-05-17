import re
def extract_date_from_string(text: str) -> str:
    # naive: find YYYY-MM-DD
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    return m.group(0) if m else text.strip()