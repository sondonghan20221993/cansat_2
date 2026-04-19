from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class ImageChunk:
    chunk_index: int
    image_paths: List[str]

    @property
    def image_count(self) -> int:
        return len(self.image_paths)

    @property
    def start_path(self) -> str:
        return self.image_paths[0]

    @property
    def end_path(self) -> str:
        return self.image_paths[-1]


def build_overlapping_chunks(
    image_paths: Sequence[str],
    chunk_size: int,
    overlap: int,
) -> List[ImageChunk]:
    if chunk_size < 2:
        raise ValueError("chunk_size must be at least 2")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    if not image_paths:
        return []

    step = chunk_size - overlap
    chunks: List[ImageChunk] = []
    start = 0
    chunk_index = 1

    while start < len(image_paths):
        end = min(start + chunk_size, len(image_paths))
        current = list(image_paths[start:end])
        if len(current) < 2:
            break
        chunks.append(ImageChunk(chunk_index=chunk_index, image_paths=current))
        if end == len(image_paths):
            break
        start += step
        chunk_index += 1

    return chunks


def flatten_chunk_summary(chunks: Iterable[ImageChunk]) -> List[dict]:
    return [
        {
            "chunk_index": chunk.chunk_index,
            "image_count": chunk.image_count,
            "start_path": chunk.start_path,
            "end_path": chunk.end_path,
            "image_paths": chunk.image_paths,
        }
        for chunk in chunks
    ]
