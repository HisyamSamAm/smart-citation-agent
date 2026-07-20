from datetime import datetime

from .models import Metadata


class CitationGenerator:

    def generate(self, metadata: Metadata, style: str, index: int = 1) -> str:
        if style == "ieee":
            return self._generate_ieee(metadata, index)
        elif style == "apa":
            return self._generate_apa(metadata)
        return ""

    def _generate_ieee(self, meta: Metadata, idx: int) -> str:
        s = f"[{idx}] "
        author_str = self._format_authors_ieee(meta.authors) if meta.authors else ""
        title = meta.title or "[Untitled]"

        if author_str:
            s += f"{author_str}, "
        s += f'"{title},"'

        if meta.source_type == "journal":
            if meta.publisher:
                s += f" {meta.publisher}"
            if meta.volume:
                s += f", vol. {meta.volume}"
            if meta.issue:
                s += f", no. {meta.issue}" if meta.volume else f" no. {meta.issue}"
            if meta.pages:
                s += f", pp. {meta.pages}"

        elif meta.source_type in ("conference", "preprint"):
            if meta.publisher:
                s += f" in {meta.publisher}"
            if meta.pages:
                s += f", pp. {meta.pages}"

        elif meta.source_type == "book":
            if meta.publisher:
                s += f" {meta.publisher}"

        elif meta.source_type == "repository":
            s += f" {meta.publisher or 'GitHub'}"
            s += " [Online]"
            if meta.url:
                s += f", Available: {meta.url}"
            s += f", Accessed: {datetime.now().strftime('%b %d, %Y')}"

        else:
            if meta.publisher:
                s += f" {meta.publisher}"
            s += " [Online]"
            if meta.url:
                s += f", Available: {meta.url}"
            s += f", Accessed: {datetime.now().strftime('%b %d, %Y')}"

        if meta.year and meta.source_type not in ("repository", "website", "blog"):
            if s.rstrip().rstrip('"').rstrip().endswith(","):
                s += f" {meta.year}"
            else:
                s += f", {meta.year}"

        return s + "."

    def _format_authors_ieee(self, authors: list[str]) -> str:
        formatted = []
        for author in authors:
            parts = author.strip().split()
            if len(parts) >= 2:
                formatted.append(f"{parts[0][0].upper()}. {' '.join(parts[1:])}")
            elif len(parts) == 1:
                formatted.append(parts[0])
        if not formatted:
            return ""
        if len(formatted) > 6:
            return f"{', '.join(formatted[:6])}, et al."
        return ", ".join(formatted)

    def _generate_apa(self, meta: Metadata) -> str:
        author_str = self._format_authors_apa(meta.authors) if meta.authors else ""
        year_str = f"({meta.year})" if meta.year else "(n.d.)"
        title = meta.title or "[Untitled]"

        s = ""

        if author_str:
            s += f"{author_str} {year_str}. "
        else:
            s += f"{year_str}. "

        s += f"{title}."

        if meta.source_type == "journal":
            journal_parts = []
            if meta.publisher:
                journal_parts.append(meta.publisher)
            if meta.volume:
                vol = meta.volume
                if meta.issue:
                    vol += f"({meta.issue})"
                journal_parts.append(vol)
            if meta.pages:
                journal_parts.append(meta.pages)
            if journal_parts:
                s += " " + ", ".join(journal_parts) + "."
            if meta.doi:
                s += f" https://doi.org/{meta.doi}"

        elif meta.source_type in ("conference", "preprint"):
            if meta.publisher:
                s += f" In {meta.publisher}."
            if meta.pages:
                s += f" pp. {meta.pages}."
            if meta.doi:
                s += f" https://doi.org/{meta.doi}"

        elif meta.source_type == "book":
            if meta.publisher:
                s += f" {meta.publisher}."
            if meta.doi:
                s += f" https://doi.org/{meta.doi}"

        elif meta.source_type == "repository":
            repo = meta.publisher or "GitHub"
            s += f" [Software]. {repo}."
            if meta.url:
                s += f" {meta.url}"

        else:
            if meta.publisher:
                s += f" {meta.publisher}."
            if meta.url:
                s += f" {meta.url}"

        return s

    def _format_authors_apa(self, authors: list[str]) -> str:
        formatted = []
        for author in authors:
            parts = author.strip().split()
            if len(parts) >= 2:
                last_name = parts[-1]
                initials = " ".join(p[0].upper() + "." for p in parts[:-1] if p)
                formatted.append(f"{last_name}, {initials}")
            elif len(parts) == 1:
                formatted.append(f"{parts[0]}.")
        if not formatted:
            return ""
        return ", ".join(formatted)
