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

        section_titles = {
            "Hotel Information",
            "Rooms",
            "Facilities",
            "Check-in and Check-out",
            "Pets",
            "Cancellation",
        }

        for paragraph in paragraphs:
            is_section_title = paragraph in section_titles

            if is_section_title:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                current_chunk = paragraph
                continue

            candidate = (
                f"{current_chunk}\n\n{paragraph}"
                if current_chunk
                else paragraph
            )

            if len(candidate) <= chunk_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
