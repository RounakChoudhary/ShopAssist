from rag.models import Document, Chunk


def chunk_document_by_headings(document: Document) -> list[Chunk]:
    chunks = []
    lines = document.content.splitlines()
    chunk_index = 0
    curr_heading = None
    curr_content = []
    for line in lines:
        if line.startswith("#"):
            if curr_heading is not None:
                chunk = Chunk(
                    filename=document.filename,
                    section_title=curr_heading,
                    chunk_index=chunk_index,
                    content="\n".join(curr_content).strip(),
                )
                chunks.append(chunk)
                chunk_index += 1
            curr_heading = line
            curr_content = []
        else:
            curr_content.append(line)
    if curr_heading is not None:
        chunk = Chunk(
            filename=document.filename,
            section_title=curr_heading,
            chunk_index=chunk_index,
            content="\n".join(curr_content),
        )
        chunks.append(chunk)

    return chunks
