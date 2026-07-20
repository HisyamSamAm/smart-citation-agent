from .models import Reference


class BibliographyBuilder:

    def assign_indices(self, refs: list[Reference], style: str) -> list[Reference]:
        for i, ref in enumerate(refs, 1):
            ref.index = i
        return refs

    def remove_duplicates(self, refs: list[Reference]) -> list[Reference]:
        seen_dois = set()
        seen_titles = set()
        unique = []
        for ref in refs:
            meta = ref.metadata
            if meta and meta.doi:
                key = meta.doi.lower()
                if key in seen_dois:
                    continue
                seen_dois.add(key)
            elif meta and meta.title:
                key = meta.title.lower().strip()
                if key in seen_titles:
                    continue
                seen_titles.add(key)
            unique.append(ref)
        return unique

    def build(self, refs: list[Reference], style: str) -> str:
        lines = []
        for ref in refs:
            lines.append(ref.citation or "")
        return "\n".join(lines)
