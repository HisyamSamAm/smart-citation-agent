import json
import re


DOI_PATTERN = re.compile(r'^10\.\d{4,}/[^\s]+$')
URL_PATTERN = re.compile(r'^https?://[^\s]+$')


class InputManager:

    def detect_type(self, raw: str) -> str:
        raw = raw.strip()
        if URL_PATTERN.match(raw):
            return "url"
        elif DOI_PATTERN.match(raw):
            return "doi"
        elif raw.startswith("{") or raw.startswith("["):
            try:
                json.loads(raw)
                return "metadata"
            except json.JSONDecodeError:
                pass
        return "title"

    def validate(self, raw: str, input_type: str) -> list[str]:
        warnings = []
        raw = raw.strip()
        if not raw:
            warnings.append("Input kosong.")
            return warnings

        if input_type == "url":
            if not URL_PATTERN.match(raw):
                warnings.append("Format URL tidak valid.")
        elif input_type == "doi":
            if not DOI_PATTERN.match(raw):
                warnings.append("Format DOI tidak valid. Gunakan format: 10.xxxx/xxxxx")
        elif input_type == "metadata":
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    if not data.get("title"):
                        warnings.append("Metadata tidak memiliki field 'title'.")
                elif isinstance(data, list):
                    if len(data) == 0:
                        warnings.append("Array referensi kosong.")
            except json.JSONDecodeError:
                warnings.append("Format JSON tidak valid.")

        return warnings
