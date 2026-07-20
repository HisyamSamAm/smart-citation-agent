from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Metadata:
    title: Optional[str] = None
    authors: list[str] = field(default_factory=list)
    year: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    source_type: str = "unknown"
    warnings: list[str] = field(default_factory=list)


@dataclass
class Reference:
    raw_input: str
    input_type: str = ""
    source_type: str = "unknown"
    metadata: Optional[Metadata] = None
    citation: Optional[str] = None
    index: int = 0
    warnings: list[str] = field(default_factory=list)
