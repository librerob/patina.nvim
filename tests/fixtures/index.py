from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    title: str
    tags: tuple[str, ...] = ()


def group_documents(documents: list[Document]) -> dict[str, list[str]]:
    """Collect titles by tag without changing the input."""
    groups: dict[str, list[str]] = {}
    for document in documents:
        for tag in document.tags or ("untagged",):
            groups.setdefault(tag, []).append(document.title)
    return groups
