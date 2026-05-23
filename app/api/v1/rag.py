from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.deps import AdminUser, get_db
from app.core.exceptions import api_response
from app.schemas import (
    DocumentUploadResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGStatsResponse,
)
from app.services.rag_service import RAGService

router = APIRouter(prefix='/rag', tags=['RAG知识检索'])


@router.post('/query', response_model=RAGQueryResponse, summary='自然语言知识检索', responses={200: {"description": "查询成功，返回检索结果"}, 401: {"description": "未登录"}, 422: {"description": "参数校验失败"}})
async def rag_query(
    request: RAGQueryRequest,
    _: AdminUser = Depends(AdminUser),
):
    svc = RAGService()
    result = svc.search(query=request.query, top_k=request.top_k)
    return {
        'query': result['query'],
        'results': [
            {'content': r['content'], 'metadata': r['metadata'], 'score': r['score']}
            for r in result['results']
        ],
        'total_results': result['total_results'],
    }


@router.post('/documents/upload', status_code=status.HTTP_201_CREATED, summary='上传文档到知识库', responses={201: {"description": "上传并索引成功"}, 400: {"description": "文件格式不支持"}, 401: {"description": "未登录"}, 422: {"description": "参数校验失败"}})
async def upload_document(
    file: Annotated[UploadFile, File(description='支持 .txt 和 .md 格式的文件')],
    title: Annotated[str, Form(description='文档标题')],
    source: Annotated[str | None, Form(description='文档来源')] = None,
    tags: Annotated[str, Form(description='逗号分隔的标签列表')] = '',
    _: AdminUser = Depends(AdminUser),
):
    allowed_extensions = {'.txt', '.md'}
    fname = file.filename or 'document.txt'
    if not any(fname.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='仅支持 .txt 和 .md 格式的文件',
        )
    file_content = await file.read()
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    svc = RAGService()
    result = await svc.ingest_document(
        file_content=file_content,
        filename=fname,
        title=title,
        source=source or '',
        tags=tag_list,
    )
    return api_response(
        data={
            'document_id': result['document_id'],
            'title': result['title'],
            'chunks_count': result['chunks_count'],
            'status': result['status'],
        },
        message='文档上传并索引成功',
        code=201,
    )


@router.post('/documents/text', status_code=status.HTTP_201_CREATED, summary='提交文本内容到知识库', responses={201: {"description": "索引成功"}, 401: {"description": "未登录"}, 422: {"description": "参数校验失败"}})
async def ingest_text_document(
    title: str = Query(..., description='文档标题'),
    content: str = Query(..., description='文档内容'),
    source: str | None = Query(None, description='文档来源'),
    tags: str | None = Query(None, description='逗号分隔的标签'),
    _: AdminUser = Depends(AdminUser),
):
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    svc = RAGService()
    result = svc.ingest_text(title=title, content=content, source=source or '', tags=tag_list)
    return api_response(
        data={
            'document_id': result['document_id'],
            'title': result['title'],
            'chunks_count': result['chunks_count'],
            'status': result['status'],
        },
        message='文本内容索引成功',
        code=201,
    )


@router.get('/documents', summary='获取已索引文档列表', responses={200: {"description": "查询成功，返回文档列表"}, 401: {"description": "未登录"}})
async def list_documents(_: AdminUser = Depends(AdminUser)):
    svc = RAGService()
    documents = svc.list_documents()
    return api_response(data=documents, message='success')


@router.delete('/documents/{document_id}', summary='删除知识库中的文档', responses={200: {"description": "删除成功"}, 401: {"description": "未登录"}, 404: {"description": "文档不存在"}})
async def delete_document(document_id: str, _: AdminUser = Depends(AdminUser)):
    svc = RAGService()
    svc.delete_document(document_id)
    return api_response(data={'document_id': document_id}, message='文档删除成功')


@router.get('/stats', response_model=RAGStatsResponse, summary='获取知识库统计信息', responses={200: {"description": "查询成功，返回统计信息"}, 401: {"description": "未登录"}})
async def get_rag_stats(_: AdminUser = Depends(AdminUser)):
    svc = RAGService()
    stats = svc.get_statistics()
    return api_response(
        data={
            'total_documents': stats.get('total_documents', 0),
            'total_chunks': stats.get('total_documents', 0),
            'collection_name': stats.get('collection_name', ''),
            'embedding_model': stats.get('embedding_model', ''),
        },
        message='查询成功',
    )
