import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .models import Metadata


CROSSREF_BASE = "https://api.crossref.org"


class MetadataAnalyzer:

    def analyze(self, raw_input: str, input_type: str, source_type: str) -> Metadata:
        if input_type == "doi":
            return self._from_doi(raw_input, source_type)
        elif input_type == "url":
            return self._from_url(raw_input, source_type)
        elif input_type == "title":
            return self._from_title(raw_input, source_type)
        elif input_type == "metadata":
            return self._from_metadata_json(raw_input, source_type)
        return Metadata(warnings=["Tipe input tidak dikenal."])

    def _from_doi(self, doi: str, source_type: str) -> Metadata:
        url = f"{CROSSREF_BASE}/works/{quote(doi, safe='')}"
        try:
            data = self._fetch_json(url)
            return self._parse_crossref(data["message"], source_type)
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            return Metadata(doi=doi, warnings=[f"CrossRef: {str(e)}"])

    def _from_url(self, url: str, source_type: str) -> Metadata:
        doi = self._extract_doi_from_url(url)
        if doi:
            result = self._from_doi(doi, source_type)
            result.url = url
            return result

        if source_type == "repository":
            repo_info = self._extract_repo_name(url)
            if repo_info:
                return Metadata(
                    title=repo_info,
                    publisher="GitHub",
                    url=url,
                    source_type=source_type,
                )

        return Metadata(url=url, source_type=source_type)

    def _from_title(self, title: str, source_type: str) -> Metadata:
        url = f"{CROSSREF_BASE}/works?query.title={quote(title)}&rows=1"
        try:
            data = self._fetch_json(url)
            items = data.get("message", {}).get("items", [])
            if items:
                best = items[0]
                score = best.get("score", 0)
                metadata = self._parse_crossref(best, source_type)
                if score < 50:
                    metadata.warnings.append(
                        f"Rendahnya skor kecocokan judul ({score:.1f}). Periksa manual."
                    )
                return metadata
            return Metadata(warnings=["CrossRef: Tidak ada hasil untuk judul tersebut."])
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            return Metadata(warnings=[f"CrossRef: {str(e)}"])

    def _from_metadata_json(self, raw: str, source_type: str) -> Metadata:
        try:
            data = json.loads(raw)
            return self._parse_manual_metadata(data, source_type)
        except json.JSONDecodeError:
            return Metadata(warnings=["Gagal parse metadata JSON."])

    def _parse_crossref(self, msg: dict, source_type_hint: str) -> Metadata:
        titles = msg.get("title", [])
        title = titles[0] if titles else None

        authors_raw = msg.get("author", [])
        authors = []
        for a in authors_raw:
            given = a.get("given", "")
            family = a.get("family", "")
            if family:
                authors.append(f"{given} {family}".strip())

        year = self._extract_year(msg)
        publisher = msg.get("publisher")
        doi = msg.get("DOI")
        container = msg.get("container-title", [])
        container_name = container[0] if container else publisher
        volume = msg.get("volume")
        issue = msg.get("issue")
        pages = msg.get("page")

        ctype = msg.get("type", "")
        detected_type = self._map_crossref_type(ctype)
        final_type = detected_type if detected_type != "unknown" else source_type_hint

        return Metadata(
            title=title,
            authors=authors,
            year=year,
            publisher=container_name or publisher,
            doi=doi,
            volume=volume,
            issue=issue,
            pages=pages,
            source_type=final_type,
        )

    def _parse_manual_metadata(self, data: dict, source_type: str) -> Metadata:
        authors_raw = data.get("author", data.get("authors", ""))
        if isinstance(authors_raw, str):
            authors = [a.strip() for a in authors_raw.split(",")]
        elif isinstance(authors_raw, list):
            authors = [str(a) for a in authors_raw]
        else:
            authors = []

        year = data.get("year")
        if year is not None:
            year = str(year)

        return Metadata(
            title=data.get("title"),
            authors=authors,
            year=year,
            publisher=data.get("publisher"),
            doi=data.get("doi"),
            url=data.get("url"),
            volume=data.get("volume"),
            issue=data.get("issue"),
            pages=data.get("pages"),
            source_type=data.get("source_type", source_type),
        )

    def _extract_year(self, msg: dict) -> str:
        for key in ("published-print", "published-online", "issued", "created"):
            date_info = msg.get(key, {})
            date_parts = date_info.get("date-parts", [])
            if date_parts and date_parts[0]:
                return str(date_parts[0][0])
        return "n.d."

    def _map_crossref_type(self, ctype: str) -> str:
        mapping = {
            "journal-article": "journal",
            "conference-paper": "conference",
            "proceedings-article": "conference",
            "book": "book",
            "book-chapter": "book",
            "dissertation": "thesis",
            "report": "report",
            "posted-content": "preprint",
            "software": "repository",
            "dataset": "dataset",
        }
        return mapping.get(ctype, "unknown")

    def _extract_doi_from_url(self, url: str) -> str:
        patterns = [
            r'doi\.org/(10\.\d{4,}/[^\s?#]+)',
            r'doi/(10\.\d{4,}/[^\s?#]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).rstrip("/")
        return ""

    def _extract_repo_name(self, url: str) -> str:
        match = re.search(r'github\.com/([^/]+/[^/?#]+)', url)
        if match:
            return match.group(1).rstrip("/")
        match = re.search(r'gitlab\.com/([^/]+/[^/?#]+)', url)
        if match:
            return match.group(1).rstrip("/")
        match = re.search(r'bitbucket\.org/([^/]+/[^/?#]+)', url)
        if match:
            return match.group(1).rstrip("/")
        return ""

    def _fetch_json(self, url: str) -> dict:
        req = Request(url, headers={
            "User-Agent": "SCRA/1.0 (mailto:scra@example.com)"
        })
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
