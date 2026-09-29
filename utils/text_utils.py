import re


def safe_filename(filename: str) -> str:
    """
    Convert text into a safe filename.
    """
    filename = filename.strip()

    if not filename:
        return "legal_document"

    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', '_', filename)

    return filename[:100]


def sanitize_text(text: str) -> str:
    """
    Clean generated document text.
    """
    if text is None:
        return ""

    text = str(text)

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text.strip()