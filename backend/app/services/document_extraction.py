from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


class DocumentExtractionService:
    """Extract text from supported document formats."""

    def extract(self, file_path: str) -> str:
        """Extract text from a document."""

        path = Path(file_path)

        extension = path.suffix.lower()

        if extension == ".pdf":
            return self._extract_pdf(path)

        if extension == ".docx":
            return self._extract_docx(path)

        if extension == ".txt":
            return self._extract_txt(path)

        raise ValueError(
            f"Unsupported document type: {extension}"
        )

    def _extract_pdf(self, path: Path) -> str:
        """Extract text from a PDF file."""

        reader = PdfReader(str(path))

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    def _extract_docx(self, path: Path) -> str:
        """Extract text from a DOCX file."""

        document = DocxDocument(str(path))

        paragraphs = []

        for paragraph in document.paragraphs:
            if paragraph.text:
                paragraphs.append(paragraph.text)

        return "\n".join(paragraphs)

    def _extract_txt(self, path: Path) -> str:
        """Extract text from a TXT file."""

        return path.read_text(
            encoding="utf-8"
        )
