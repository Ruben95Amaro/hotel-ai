from pathlib import Path


class DocumentService:
    def load_document(self, file_path: str) -> str:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        return path.read_text(encoding="utf-8")

    def split_into_chunks(
        self,
        text: str,
        chunk_size: int = 500,
    ) -> list[str]:
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if not current_chunk:
                current_chunk = paragraph
                continue

            candidate = f"{current_chunk}\n\n{paragraph}"

            if len(candidate) <= chunk_size:
                current_chunk = candidate
            else:
                chunks.append(current_chunk)
                current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return chunks