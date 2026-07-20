import json
import re


class SourceDetector:

    ACADEMIC_DOMAINS = {
        "ieee.org": "journal",
        "acm.org": "journal",
        "springer.com": "journal",
        "link.springer.com": "journal",
        "sciencedirect.com": "journal",
        "tandfonline.com": "journal",
        "wiley.com": "journal",
        "nature.com": "journal",
        "science.org": "journal",
        "sagepub.com": "journal",
        "oxfordjournals.org": "journal",
        "cambridge.org": "journal",
        "mdpi.com": "journal",
        "frontiersin.org": "journal",
        "plos.org": "journal",
        "arxiv.org": "preprint",
        "biorxiv.org": "preprint",
        "medrxiv.org": "preprint",
        "github.com": "repository",
        "gitlab.com": "repository",
        "bitbucket.org": "repository",
        "wikipedia.org": "website",
        "medium.com": "blog",
        "blogspot.com": "blog",
        "wordpress.com": "blog",
    }

    ACADEMIC_TLDS = {".ac.id", ".ac.uk", ".ac.jp", ".edu", ".edu.au", ".edu.cn"}

    def detect(self, raw_input: str, input_type: str) -> str:
        if input_type == "url":
            return self._detect_from_url(raw_input)
        elif input_type == "doi":
            return "journal"
        elif input_type == "title":
            return "journal"
        elif input_type == "metadata":
            try:
                data = json.loads(raw_input)
                if isinstance(data, list):
                    return "multiple"
                if isinstance(data, dict):
                    return data.get("source_type", "journal")
            except Exception:
                pass
        return "unknown"

    def _detect_from_url(self, url: str) -> str:
        domain = self._extract_domain(url)
        for key, stype in self.ACADEMIC_DOMAINS.items():
            if key in domain:
                return stype
        for tld in self.ACADEMIC_TLDS:
            if domain.endswith(tld):
                return "journal"
        return "website"

    def _extract_domain(self, url: str) -> str:
        match = re.search(r'https?://([^/]+)', url)
        return match.group(1).lower() if match else url.lower()
