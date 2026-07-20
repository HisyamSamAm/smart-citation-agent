from .models import Reference


class OutputValidator:

    def validate(self, refs: list[Reference], style: str) -> list[str]:
        issues = []
        for i, ref in enumerate(refs, 1):
            if ref.index != i:
                issues.append(f"Ketidaksesuaian index pada referensi {i}: index={ref.index}")
        for ref in refs:
            if not ref.citation:
                issues.append(f"Referensi {ref.index}: citation kosong.")
        return issues
