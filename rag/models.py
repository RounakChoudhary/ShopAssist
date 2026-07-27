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