from pathlib import Path
from rag.models import Document


def get_policy_files(folder: Path):
    files = []
    for file in folder.iterdir():
        if file.suffix == ".md":
            files.append(file)
    return files

def read_policy_files(files: list[Path]) -> list[Document]:
    documents = []

    for file in files:
        document = Document(
            filename=file.name,
            content=file.read_text(encoding="utf-8")
        )
        documents.append(document)

    return documents

