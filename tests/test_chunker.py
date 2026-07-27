from pathlib import Path
from rag.chunker import chunk_document_by_headings
from rag.loader import get_policy_files , read_policy_files



def main():
    folder = Path("data/policies")
    files = get_policy_files(folder)
    docs = read_policy_files(files)
    for doc  in docs:
        print("="*70)
        print(f"document name {doc.filename}")
        chunks = chunk_document_by_headings(doc)
        for chunk in chunks :
            print("-"*50)
            print(f"Chunk Index : {chunk.chunk_index}")
            print(f"Section     : {chunk.section_title}")
            print("Content:")
            print(chunk.content)
            print()



if __name__ == "__main__":
    main()