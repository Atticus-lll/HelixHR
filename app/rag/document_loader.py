import re
from typing import Generator, Optional

import aiofiles


class DocumentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        if len(text) <= self.chunk_size:
            return [text]
        # Step 1: Try semantic chunking (split by numbered section headers)
        sections = self._split_by_sections(text)
        if len(sections) > 1:
            chunks: list[str] = []
            for section in sections:
                if len(section) <= self.chunk_size:
                    chunks.append(section)
                else:
                    # Fallback: character-based chunk for oversized sections
                    chunks.extend(self._fixed_chunk(section))
            return [c for c in chunks if c.strip()]
        # Step 2: Fallback to fixed-size character chunking
        return self._fixed_chunk(text)

    def _split_by_sections(self, text: str) -> list[str]:
        section_pattern = r"(?=^\d+\.\d?\s|\n\d+\.\d?\s)"
        parts = re.split(section_pattern, text, flags=re.MULTILINE)
        # Merge short leading fragments into the next section
        merged: list[str] = []
        buffer = ""
        for part in parts:
            if re.match(r"^\d+\.\d?\s", part.strip()):
                if buffer.strip():
                    merged.append(buffer.strip())
                buffer = part
            else:
                buffer += part
        if buffer.strip():
            merged.append(buffer.strip())
        return merged

    def _fixed_chunk(self, text: str) -> list[str]:
        chunks: list[str] = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            if end < text_len and end - start >= self.chunk_overlap:
                boundary = text[start + self.chunk_overlap : end]
                last_space = boundary.rfind(" ")
                if last_space != -1:
                    end = start + self.chunk_overlap + last_space
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= text_len:
                break
            start = start + self.chunk_size - self.chunk_overlap
        return chunks


async def load_text_file(content: bytes, filename: str) -> tuple[str, str]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("gbk")
        except UnicodeDecodeError:
            text = content.decode("utf-8", errors="replace")
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return filename, text


def extract_text_from_content(content: str, source: str, title: str) -> str:
    header = "【文档标题】{}\n【来源】{}\n\n".format(title, source) if title or source else ""
    return header + content
