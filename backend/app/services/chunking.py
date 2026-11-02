from app.schemas.chunk import TextChunk
from app.schemas.document import IngestedDocument


class ChunkingService:
    def __init__(
        self,
        chunk_size_words: int = 180,
        overlap_words: int = 30,
    ) -> None:
        if chunk_size_words <= 0:
            raise ValueError("chunk_size_words must be positive.")

        if overlap_words < 0:
            raise ValueError("overlap_words cannot be negative.")

        if overlap_words >= chunk_size_words:
            raise ValueError("overlap_words must be smaller than chunk_size_words.")

        self.chunk_size_words = chunk_size_words
        self.overlap_words = overlap_words

    def chunk_document(
        self,
        document: IngestedDocument,
    ) -> list[TextChunk]:
        chunks: list[TextChunk] = []

        for page in document.pages:
            words = page.text.split()

            if not words:
                continue

            start_word = 0
            chunk_index = 0

            while start_word < len(words):
                end_word = min(
                    start_word + self.chunk_size_words,
                    len(words),
                )

                chunk_text = " ".join(words[start_word:end_word])

                chunks.append(
                    TextChunk(
                        chunk_id=(
                            f"{document.document_id}:"
                            f"p{page.page_number}:c{chunk_index}"
                        ),
                        document_id=document.document_id,
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        start_word=start_word,
                        end_word=end_word,
                        text=chunk_text,
                    )
                )

                if end_word == len(words):
                    break

                start_word = end_word - self.overlap_words
                chunk_index += 1

        return chunks