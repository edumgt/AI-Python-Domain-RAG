from pathlib import Path

from pypdf import PdfReader

from app.utils.text_cleaner import clean_text


class FileParser:
    def parse_file(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".txt":
            text = path.read_text(encoding="utf-8", errors="ignore")
            return clean_text(text)

        if suffix == ".pdf":
            return self._parse_pdf(path)

        raise ValueError(f"unsupported file type: {suffix}")

    def _parse_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages = []

        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            if page_text:
                pages.append(page_text)

        return clean_text("\n\n".join(pages))
