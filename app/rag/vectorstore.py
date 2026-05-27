import json
from pathlib import Path
from typing import Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.embeddings import get_embedding_model


def _tokenize(text: str) -> list[str]:
    import re, jieba
    text = text.lower()
    text = re.sub(r'[^\u4e00-\u9fffa-z0-9]', ' ', text)
    return list(jieba.cut(text))


def _rerank_hybrid(
    chunks: list[dict[str, Any]],
    vector_scores: list[float],
    bm25_scores: list[float],
    bm25_weight: float = 0.7,
) -> list[dict[str, Any]]:
    combined = []
    for i, c in enumerate(chunks):
        fused = bm25_weight * bm25_scores[i] + (1 - bm25_weight) * vector_scores[i]
        new_chunk = dict(c)
        new_chunk["fused_score"] = fused
        combined.append((fused, i, new_chunk))
    combined.sort(key=lambda x: x[0], reverse=True)
    return [item for _, _, item in combined]


def _bm25_score(query: str, chunks: list[dict[str, Any]], index: Any) -> list[float]:
    tokens = _tokenize(query)
    scores = index.get_scores(tokens)
    return scores.tolist()


def _normalize_scores(scores: list[float]) -> list[float]:
    mn, mx = min(scores), max(scores)
    if mx == mn:
        return [1.0] * len(scores) if mx > 0 else [0.0] * len(scores)
    return [(s - mn) / (mx - mn) for s in scores]


chroma_client: Optional[chromadb.PersistentClient] = None

_bm25_index: Optional[Any] = None
_bm25_chunks: Optional[list[dict[str, Any]]] = None


def get_chroma_client() -> chromadb.PersistentClient:
    global chroma_client
    if chroma_client is None:
        persist_dir = Path(settings.rag.persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)
        chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
    return chroma_client


def get_or_create_collection() -> chromadb.Collection:
    client = get_chroma_client()
    try:
        collection = client.get_collection(name=settings.rag.collection_name)
    except Exception:
        collection = client.create_collection(
            name=settings.rag.collection_name,
            metadata={"description": "HelixHR document knowledge base"},
        )
    return collection


def add_documents(
    document_id: str,
    title: str,
    chunks: list[str],
    metadata: dict[str, Any],
) -> int:
    collection = get_or_create_collection()
    embed_model = get_embedding_model()
    embeddings = embed_model.embed_texts(chunks)
    chunk_ids = ["{}_chunk_{}".format(document_id, i) for i in range(len(chunks))]
    chunk_metadata = []
    for i, chunk in enumerate(chunks):
        meta = {}
        for k, v in metadata.items():
            if k == "tags":
                meta[k] = json.dumps(v) if v else ""
            elif v is None:
                meta[k] = ""
            else:
                meta[k] = v
        meta["chunk_index"] = i
        meta["document_id"] = document_id
        chunk_metadata.append(meta)
    collection.add(ids=chunk_ids, embeddings=embeddings, documents=chunks, metadatas=chunk_metadata)
    return len(chunks)


def _get_bm25_index() -> tuple[Any, list[dict[str, Any]]]:
    global _bm25_index, _bm25_chunks
    if _bm25_index is not None:
        return _bm25_index, _bm25_chunks

    collection = get_or_create_collection()
    all_data = collection.get(include=["documents", "metadatas"])
    if not all_data or not all_data["ids"]:
        _bm25_chunks = []
        return None, []

    from rank_bm25 import BM25Okapi
    _bm25_chunks = []
    texts = []
    for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
        chunk = {"content": doc, "metadata": meta}
        _bm25_chunks.append(chunk)
        tokens = _tokenize(doc)
        texts.append(tokens)

    _bm25_index = BM25Okapi(texts)
    return _bm25_index, _bm25_chunks


def similarity_search(
    query: str,
    top_k: int | None = None,
    filter_metadata: dict[str, Any] | None = None,
    threshold: float = 0.3,
) -> list[dict[str, Any]]:
    collection = get_or_create_collection()
    embed_model = get_embedding_model()
    query_embedding = embed_model.embed_text(query)
    k = top_k or settings.rag.top_k

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"ChromaDB query failed: {e}")
        return []

    if not results["documents"] or not results["documents"][0]:
        return []

    raw_chunks = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        raw_chunks.append({"content": doc, "metadata": meta, "distance": distance})

    vector_scores = [max(0, 1 - (c["distance"] ** 2) / 2) for c in raw_chunks]

    bm25_index, bm25_chunks = _get_bm25_index()
    if bm25_index is not None and bm25_chunks:
        all_bm25_scores = _bm25_score(query, bm25_chunks, bm25_index)
        content_to_idx = {c["content"]: i for i, c in enumerate(bm25_chunks)}
        bm25_scores_for_results = [all_bm25_scores[content_to_idx[c["content"]]] for c in raw_chunks]
        bm25_all_min = min(all_bm25_scores)
        bm25_all_max = max(all_bm25_scores)
        if bm25_all_max != bm25_all_min:
            bm25_normalized = [(s - bm25_all_min) / (bm25_all_max - bm25_all_min) for s in bm25_scores_for_results]
        else:
            bm25_normalized = [0.0] * len(bm25_scores_for_results)
        vector_normalized = _normalize_scores(vector_scores)
        reranked = _rerank_hybrid(raw_chunks, vector_normalized, bm25_normalized)
    else:
        reranked = sorted(raw_chunks, key=lambda x: x["distance"])

    output = []
    for c in reranked:
        score = c.get("fused_score", max(0, 1 - (c["distance"] ** 2) / 2))
        if score >= threshold:
            output.append({
                "content": c["content"],
                "metadata": c["metadata"],
                "score": round(score, 4),
            })
    return output


def get_collection_stats() -> dict[str, Any]:
    client = get_chroma_client()
    try:
        collection = client.get_collection(name=settings.rag.collection_name)
        return {
            "total_documents": collection.count(),
            "collection_name": collection.name,
            "embedding_model": settings.rag.embedding_model,
        }
    except Exception:
        return {
            "total_documents": 0,
            "collection_name": settings.rag.collection_name,
            "embedding_model": settings.rag.embedding_model,
        }


def delete_document_chunks(document_id: str) -> None:
    collection = get_or_create_collection()
    try:
        results = collection.get(where={"document_id": document_id})
        if results and results["ids"]:
            collection.delete(ids=results["ids"])
    except Exception:
        pass


def list_documents() -> list[dict[str, Any]]:
    collection = get_or_create_collection()
    try:
        all_data = collection.get(include=["metadatas"])
        if not all_data or not all_data["ids"]:
            return []
        doc_map: dict[str, dict] = {}
        for meta in all_data["metadatas"]:
            doc_id = meta.get("document_id", "")
            if doc_id and doc_id not in doc_map:
                doc_map[doc_id] = {
                    "document_id": doc_id,
                    "title": meta.get("title", ""),
                    "source": meta.get("source", ""),
                    "tags": [],
                    "chunks_count": 0,
                    "created_at": meta.get("created_at", ""),
                }
                if doc_id:
                    raw_tags = meta.get("tags", "[]")
                    if isinstance(raw_tags, str) and raw_tags:
                        try:
                            doc_map[doc_id]["tags"] = json.loads(raw_tags)
                        except Exception:
                            doc_map[doc_id]["tags"] = []
                    elif isinstance(raw_tags, list):
                        doc_map[doc_id]["tags"] = raw_tags
                if doc_id:
                    doc_map[doc_id]["chunks_count"] += 1
        return list(doc_map.values())
    except Exception:
        return []


def reset_collection() -> None:
    global _bm25_index, _bm25_chunks
    _bm25_index = None
    _bm25_chunks = None
    client = get_chroma_client()
    try:
        client.delete_collection(name=settings.rag.collection_name)
    except Exception:
        pass
    get_or_create_collection()
