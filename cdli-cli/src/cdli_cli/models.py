"""Data models and enums for CDLI CLI."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    """Supported output formats for metadata."""
    JSON = "json"
    JSONLD = "jsonld"
    RDF = "rdf"
    TURTLE = "turtle"
    NTRIPLES = "ntriples"


class InscriptionFormat(str, Enum):
    """Supported formats for inscription exports."""
    ATF = "atf"
    CONLL = "conll"
    CONLLU = "conllu"


class BibliographyFormat(str, Enum):
    """Supported formats for bibliography exports."""
    BIBTEX = "bibtex"
    RIS = "ris"
    CSLJSON = "csljson"
    FORMATTED = "formatted"


class TabularFormat(str, Enum):
    """Supported formats for tabular exports."""
    CSV = "csv"
    TSV = "tsv"
    XLSX = "xlsx"


class EntityType(str, Enum):
    """CDLI entity types."""
    TABLET = "cdli-tablet"
    ARTIFACT = "artifacts"
    PUBLICATION = "publications"
    INSCRIPTION = "inscriptions"
    COLLECTION = "collections"
    ARCHIVE = "archives"
    PERIOD = "periods"
    GENRE = "genres"
    MATERIAL = "materials"
    OBJECT_TYPE = "object-types"
    LANGUAGE = "languages"
    SCRIPT = "scripts"
    PROVENANCE = "proveniences"
    REGION = "regions"
    PERSON = "persons"
    AUTHOR = "authors"
    LOCATION = "locations"
    DYNASTY = "dynasties"
    RULER = "rulers"
    JOURNAL = "journals"
    ABBREVIATION = "abbreviations"
    PLACE = "places"


# MIME type mappings
FORMAT_MIME_TYPES: dict[str, str] = {
    # Metadata formats
    "json": "application/json",
    "jsonld": "application/ld+json",
    "rdf": "application/rdf+xml",
    "turtle": "text/turtle",
    "ntriples": "application/n-triples",
    "rdfjson": "application/rdf+json",
    # Inscription formats
    "atf": "text/x-c-atf",
    "conll": "text/x-cdli-conll",
    "conllu": "text/x-conll-u",
    # Bibliography formats
    "bibtex": "application/x-bibtex",
    "ris": "application/x-research-info-systems",
    "csljson": "application/vnd.citationstyles.csl+json",
    "formatted": "text/x-bibliography",
    # Tabular formats
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

# File extensions for formats
FORMAT_EXTENSIONS: dict[str, str] = {
    "json": ".json",
    "jsonld": ".jsonld",
    "rdf": ".rdf",
    "turtle": ".ttl",
    "ntriples": ".nt",
    "bibtex": ".bib",
    "ris": ".ris",
    "csv": ".csv",
    "tsv": ".tsv",
    "xlsx": ".xlsx",
    "atf": ".atf",
    "conll": ".conll",
    "conllu": ".conllu",
}


class TabletSummary(BaseModel):
    """Summary information for a CDLI tablet."""
    id: str
    designation: Optional[str] = None
    period: Optional[str] = None
    provenance: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    collection: Optional[str] = None


class SearchResult(BaseModel):
    """Search result from CDLI."""
    total: int = 0
    page: int = 1
    per_page: int = 25
    results: list[dict[str, Any]] = Field(default_factory=list)


class CDLIError(Exception):
    """Base exception for CDLI CLI errors."""
    pass


class APIError(CDLIError):
    """API request error."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


class NotFoundError(CDLIError):
    """Resource not found error."""
    pass