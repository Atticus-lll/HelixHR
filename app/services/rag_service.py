from typing import Any

from app.core.exceptions import NotFoundException
from app.rag.retriever import (
    get_document_list,
    get_stats,
    index_document,
    index_uploaded_document,
    remove_document,
    retrieve,
)


class RAGService:
    def search(self, query: str, top_k: int | None = None) -> dict[str, Any]:
        return retrieve(query=query, top_k=top_k)

    async def ingest_document(
        self,
        file_content: bytes,
        filename: str,
        title: str,
        source: str = "",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        return await index_uploaded_document(
            file_content=file_content,
            filename=filename,
            title=title,
            source=source,
            tags=tags,
        )

    def ingest_text(
        self,
        title: str,
        content: str,
        source: str = "",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        return index_document(title=title, content=content, source=source, tags=tags)

    def list_documents(self) -> list[dict[str, Any]]:
        return get_document_list()

    def get_statistics(self) -> dict[str, Any]:
        return get_stats()

    def delete_document(self, document_id: str) -> bool:
        result = remove_document(document_id)
        if not result:
            raise NotFoundException("文档不存在或已删除")
        return result
