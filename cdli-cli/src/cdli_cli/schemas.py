"""Pydantic schemas for CDLI data structures."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Period(BaseModel):
    """Historical period information."""
    id: int
    sequence: int
    period: str


class Publication(BaseModel):
    """Publication information."""
    id: int
    designation: Optional[str] = None
    bibtexkey: Optional[str] = None
    year: Optional[str] = None
    entry_type_id: Optional[int] = None
    address: Optional[str] = None
    number: Optional[str] = None
    publisher: Optional[str] = None
    title: Optional[str] = None
    series: Optional[str] = None
    author: Optional[str] = None


class Composite(BaseModel):
    """Composite text information."""
    id: int
    composite_no: str
    designation: Optional[str] = None
    dates_referenced: Optional[str] = None
    artifact_comments: Optional[str] = None
    created_by: Optional[int] = None
    artifact_type_comments: Optional[str] = None


class CompositeLink(BaseModel):
    """Link between artifact and composite."""
    id: int
    composite_no: str
    artifact_id: int
    composite: Composite


class Inscription(BaseModel):
    """Inscription/text content."""
    id: int
    artifact_id: int
    atf: str
    is_atf2conll_diff_resolved: Optional[bool] = None
    is_latest: bool = True


class ArtifactPublicationLink(BaseModel):
    """Link between artifact and publication."""
    id: int
    entity_id: int
    publication_id: int
    exact_reference: Optional[str] = None
    publication_type: str
    table_name: str
    publication: Optional[Publication] = None


class Artifact(BaseModel):
    """Complete artifact/tablet data."""
    id: int
    designation: Optional[str] = None
    excavation_no: Optional[str] = None
    museum_no: Optional[str] = None
    findspot_comments: Optional[str] = None
    findspot_square: Optional[str] = None
    thickness: Optional[str] = None
    height: Optional[str] = None
    width: Optional[str] = None
    dates_referenced: Optional[str] = None
    created_by: Optional[int] = None
    period: Optional[Period] = None
    seals: list[Any] = Field(default_factory=list)
    composites: list[CompositeLink] = Field(default_factory=list)
    impressions: list[Any] = Field(default_factory=list)
    witnesses: list[Any] = Field(default_factory=list)
    inscription: Optional[Inscription] = None
    publications: list[ArtifactPublicationLink] = Field(default_factory=list)


class Collection(BaseModel):
    """Museum collection information."""
    id: int
    name: str
    abbreviation: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class Provenance(BaseModel):
    """Find location information."""
    id: int
    provenance: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None


class Genre(BaseModel):
    """Text genre information."""
    id: int
    genre: str
    description: Optional[str] = None


class Language(BaseModel):
    """Language information."""
    id: int
    language: str
    family: Optional[str] = None
    writing_system: Optional[str] = None


class Material(BaseModel):
    """Material information."""
    id: int
    material: str