from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from app.schemas.chunk import TextChunk
from app.schemas.document import IngestedDocument
from app.schemas.search import SearchRequest, SearchResult
from app.services.chunking import ChunkingService
from app.services.document_store import InMemoryDocumentStore
from app.services.embedding_service import EmbeddingService
from app.services.pdf_ingestion import (
    PDFIngestionError,
    PDFIngestionService,
)
from app.services.vector_store import InMemoryVectorStore

router = APIRouter(prefix="/documents", tags=["Documents"])

ingestion_service = PDFIngestionService()
chunking_service = ChunkingService()
document_store = InMemoryDocumentStore()
embedding_service = EmbeddingService()
vector_store = InMemoryVectorStore()


@router.post(
    "/upload",
    response_model=IngestedDocument,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
) -> IngestedDocument:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    file_bytes = await file.read()

    try:
        document = ingestion_service.ingest(
            filename=file.filename,
            file_bytes=file_bytes,
        )

        document_store.save(document)

        chunks = chunking_service.chunk_document(document)
        embedded_chunks = embedding_service.embed_chunks(chunks)
        vector_store.add(embedded_chunks)

        return document

    except PDFIngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()


@router.get(
    "",
    response_model=list[IngestedDocument],
)
def list_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[IngestedDocument]:
    return document_store.list_all(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{document_id}",
    response_model=IngestedDocument,
)
def get_document(document_id: str) -> IngestedDocument:
    document = document_store.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


@router.get(
    "/{document_id}/chunks",
    response_model=list[TextChunk],
)
def get_document_chunks(document_id: str) -> list[TextChunk]:
    document = document_store.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return chunking_service.chunk_document(document)


@router.post(
    "/search",
    response_model=list[SearchResult],
)
def search_documents(
    request: SearchRequest,
) -> list[SearchResult]:
    query_embedding = embedding_service.embed_query(request.query)

    return vector_store.search(
        query_embedding=query_embedding,
        top_k=request.top_k,
        document_id=request.document_id,
        min_score=request.min_score,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
)
def delete_document(document_id: str) -> dict[str, str | int]:
    document = document_store.delete(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    deleted_chunks = vector_store.delete_document(document_id)

    return {
        "document_id": document_id,
        "deleted_chunks": deleted_chunks,
    }