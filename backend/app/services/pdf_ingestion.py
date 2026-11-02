
from hashlib import sha256
from io import BytesIO
from uuid import uuid4

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.schemas.document import IngestedDocument, PageContent


MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024


class PDFIngestionError(Exception):
    """Base exception for PDF ingestion failures."""


class InvalidPDFError(PDFIngestionError):
    """Raised when the uploaded file is not a valid PDF."""


class EncryptedPDFError(PDFIngestionError):
    """Raised when the PDF cannot be decrypted."""


class EmptyPDFError(PDFIngestionError):
    """Raised when no extractable text is found."""


class PDFIngestionService:
    """Extract structured text and metadata from PDF documents."""

    def ingest(
        self,
        filename: str,
        file_bytes: bytes,
    ) -> IngestedDocument:

        self._validate_file(filename, file_bytes)

        content_fingerprint = sha256(file_bytes).hexdigest()

        try:
            reader = PdfReader(BytesIO(file_bytes))

            if reader.is_encrypted:
                decrypted = reader.decrypt("")

                if not decrypted:
                    raise EncryptedPDFError(
                        "Password-protected PDFs are not supported."
                    )

            pages = []

            for page_number, page in enumerate(reader.pages, start=1):
                extracted_text = page.extract_text() or ""

                pages.append(
                    PageContent(
                        page_number=page_number,
                        text=extracted_text.strip(),
                    )
                )

        except EncryptedPDFError:
            raise

        except (PdfReadError, ValueError, OSError) as exc:
            raise InvalidPDFError(
                "The uploaded PDF could not be read."
            ) from exc

        total_characters = sum(
            len(page.text) for page in pages
        )

        if total_characters == 0:
            raise EmptyPDFError(
                "The PDF contains no extractable text."
            )

        return IngestedDocument(
            document_id=str(uuid4()),
            filename=filename,
            content_sha256=content_fingerprint,
            page_count=len(pages),
            extracted_characters=total_characters,
            pages=pages,
        )

    @staticmethod
    def _validate_file(
        filename: str,
        file_bytes: bytes,
    ) -> None:

        if not filename.lower().endswith(".pdf"):
            raise InvalidPDFError(
                "Only PDF files are supported."
            )

        if not file_bytes:
            raise InvalidPDFError(
                "The uploaded file is empty."
            )

        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise InvalidPDFError(
                "The PDF exceeds the 25 MB size limit."
            )

        if not file_bytes.startswith(b"%PDF-"):
            raise InvalidPDFError(
                "The uploaded file is not a valid PDF."
            )
