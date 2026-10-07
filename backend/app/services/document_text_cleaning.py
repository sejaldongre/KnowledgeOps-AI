import re


class DocumentTextCleaningService:
    """Clean extracted document text before chunking."""

    def clean(self, text: str) -> str:
        """Normalize extracted text."""

        if not text:
            return ""

        text = self._normalize_line_endings(text)
        text = self._remove_null_characters(text)
        text = self._normalize_whitespace(text)
        text = self._normalize_blank_lines(text)

        return text.strip()

    def _normalize_line_endings(self, text: str) -> str:
        """Normalize different line-ending formats."""

        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _remove_null_characters(self, text: str) -> str:
        """Remove null characters from extracted text."""

        return text.replace("\x00", "")

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize unnecessary spaces and tabs."""

        lines = []

        for line in text.split("\n"):
            line = re.sub(r"[ \t]+", " ", line)
            lines.append(line.strip())

        return "\n".join(lines)

    def _normalize_blank_lines(self, text: str) -> str:
        """Limit consecutive blank lines."""

        return re.sub(r"\n{3,}", "\n\n", text)
