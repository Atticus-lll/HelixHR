from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description='查询内容')
    top_k: Optional[int] = Field(5, ge=1, le=20, description='返回结果数量')
    filter_metadata: Optional[dict[str, Any]] = Field(None, description='元数据过滤条件')


class RAGQueryChunk(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    metadata: dict[str, Any]
    score: float


class RAGQueryResponse(BaseModel):
    query: str
    results: list[RAGQueryChunk]
    total_results: int


class DocumentUploadResponse(BaseModel):
    document_id: str
    title: str
    chunks_count: int
    status: str = 'indexed'


class DocumentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    title: str
    source: Optional[str] = None
    tags: list[str]
    chunks_count: int
    created_at: str


class RAGStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    collection_name: str
    embedding_model: str
