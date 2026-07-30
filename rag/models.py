from dataclasses import dataclass


@dataclass
class Document:
    filename: str
    content: str


@dataclass
class Chunk:
    filename: str
    section_title: str
    chunk_index: int
    content: str


@dataclass
class EmbeddedChunk:
    chunk: Chunk
    embedding: list[float]


@dataclass
class RetrievedChunk:
    content: str
    filename: str
    section_title: str
    chunk_index: int
    score: float