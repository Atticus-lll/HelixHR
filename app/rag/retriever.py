from datetime import datetime
from typing import Any

from app.config import settings
from app.rag.document_loader import (
    DocumentChunker,
    extract_text_from_content,
    load_text_file,
)
from app.rag.embeddings import get_embedding_model
from app.rag.vectorstore import (
    add_documents,
    delete_document_chunks,
    get_collection_stats,
    list_documents,
    similarity_search,
)

chunker = DocumentChunker(
    chunk_size=settings.rag.chunk_size,
    chunk_overlap=settings.rag.chunk_overlap,
)


def index_document(
    title: str,
    content: str,
    source: str = "",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    doc_content = extract_text_from_content(content, source, title)
    chunks = chunker.chunk_text(doc_content)
    if not chunks:
        return {"document_id": "", "chunks_count": 0, "status": "no_content"}
    embed_model = get_embedding_model()
    document_id = embed_model.generate_document_id(title, doc_content)
    metadata = {
        "title": title,
        "source": source or "",
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
        "document_id": document_id,
    }
    chunks_count = add_documents(
        document_id=document_id,
        title=title,
        chunks=chunks,
        metadata=metadata,
    )
    return {"document_id": document_id, "title": title, "chunks_count": chunks_count, "status": "indexed"}


async def index_uploaded_document(
    file_content: bytes,
    filename: str,
    title: str,
    source: str = "",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    _, text = await load_text_file(file_content, filename)
    title = title or filename.rsplit(".", 1)[0]
    return index_document(title=title, content=text, source=source, tags=tags)


def retrieve(
    query: str,
    top_k: int | None = None,
    filter_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    k = top_k or settings.rag.top_k
    threshold = settings.rag.similarity_threshold
    results = similarity_search(query=query, top_k=k, filter_metadata=filter_metadata, threshold=threshold)
    return {"query": query, "results": results, "total_results": len(results)}


def get_stats() -> dict[str, Any]:
    return get_collection_stats()


def get_document_list() -> list[dict[str, Any]]:
    return list_documents()


def remove_document(document_id: str) -> bool:
    existing = list_documents()
    doc_exists = any(d["document_id"] == document_id for d in existing)
    if not doc_exists:
        return False
    delete_document_chunks(document_id)
    return True
