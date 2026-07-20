class MetadataValidator:

    def validate(self, metadata) -> None:
        if not metadata.title:
            metadata.warnings.append("Title tidak ditemukan.")
        if not metadata.authors:
            metadata.warnings.append("Author tidak ditemukan.")
        if not metadata.year or metadata.year == "n.d.":
            if metadata.year != "n.d.":
                metadata.warnings.append("Year tidak ditemukan. Gunakan 'n.d.'")
                metadata.year = "n.d."
        if not metadata.publisher and not metadata.doi and not metadata.url:
            metadata.warnings.append("Publisher tidak ditemukan.")
