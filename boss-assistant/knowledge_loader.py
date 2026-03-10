"""
Load knowledge context from knowledge/vision_context.md and optionally from knowledge/pdfs/.
No AI calls; safe to call from any path. Missing files return "".
"""
from pathlib import Path

DEFAULT_KNOWLEDGE_FILE = Path(__file__).resolve().parent / "knowledge" / "vision_context.md"
DEFAULT_PDFS_DIR = Path(__file__).resolve().parent / "knowledge" / "pdfs"


def _extract_text_from_pdf(path: Path) -> str:
    """Extract text from one PDF; return "" on error or if pypdf not installed."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(path)
        parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        return "\n".join(parts).strip()
    except Exception:
        return ""


def load_pdf_context(max_chars: int = 6000, pdfs_dir: Path | None = None) -> str:
    """
    Read all .pdf files in knowledge/pdfs/, extract text, and return combined text up to max_chars.
    If the folder is missing, pypdf is not installed, or no PDFs exist, return "" without raising.
    """
    dir_path = pdfs_dir if pdfs_dir is not None else DEFAULT_PDFS_DIR
    if not dir_path.is_dir():
        return ""
    pdfs = sorted(dir_path.glob("*.pdf"))
    if not pdfs:
        return ""
    combined = []
    total = 0
    for p in pdfs:
        if total >= max_chars:
            break
        text = _extract_text_from_pdf(p)
        if not text:
            continue
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.rstrip() for line in text.splitlines()]
        text = "\n".join(lines).strip()
        if total + len(text) > max_chars:
            text = text[: max_chars - total]
        if text:
            combined.append(f"[From: {p.name}]\n{text}")
            total += len(text)
    return "\n\n".join(combined) if combined else ""


def load_knowledge_context(max_chars: int = 8000) -> str:
    """
    Read knowledge/vision_context.md, normalize text, and return up to max_chars.
    If the file is missing or unreadable, return "" without raising.
    """
    path = DEFAULT_KNOWLEDGE_FILE
    if not path.is_file():
        return ""

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return ""

    # Normalize newlines to \n
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace per line, then join
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    # Strip leading/trailing whitespace of whole text
    text = text.strip()

    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def load_full_knowledge_context(
    vision_max_chars: int = 8000,
    pdf_max_chars: int = 6000,
) -> str:
    """
    Load vision_context.md and all PDFs from knowledge/pdfs/, combined for the model.
    Order: vision_context first, then "Documents (PDFs):" and PDF text. Safe if files or pypdf missing.
    """
    vision = load_knowledge_context(max_chars=vision_max_chars)
    pdf_text = load_pdf_context(max_chars=pdf_max_chars)
    if not vision.strip() and not pdf_text.strip():
        return ""
    parts = []
    if vision.strip():
        parts.append(vision.strip())
    if pdf_text.strip():
        parts.append("Documents (PDFs):\n\n" + pdf_text.strip())
    return "\n\n".join(parts)
