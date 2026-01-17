"""CDLI API client implementation."""

import sys
from pathlib import Path
from typing import Any, Optional, Union

import httpx

from .models import (
    APIError,
    BibliographyFormat,
    EntityType,
    FORMAT_EXTENSIONS,
    FORMAT_MIME_TYPES,
    InscriptionFormat,
    NotFoundError,
    OutputFormat,
    SearchResult,
    TabularFormat,
)


class CDLIClient:
    """Client for interacting with the CDLI REST API."""

    BASE_URL = "https://cdli.earth"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the CDLI client.

        Args:
            base_url: Override the default CDLI base URL
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"User-Agent": "cdli-cli/0.1.0"},
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "CDLIClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _get_accept_header(self, format_name: str) -> str:
        """Get the Accept header value for a format."""
        return FORMAT_MIME_TYPES.get(format_name, "application/json")

    def _handle_response(
        self,
        response: httpx.Response,
        binary: bool = False,
    ) -> Union[dict[str, Any], str, bytes]:
        """Handle API response and errors."""
        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {response.url}")
        if response.status_code >= 400:
            raise APIError(response.status_code, response.text)

        if binary:
            return response.content

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    # =========================================================================
    # Core Entity Methods
    # =========================================================================

    def get_entity(
        self,
        entity_type: EntityType,
        entity_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """
        Get an entity by type and ID.

        Args:
            entity_type: The type of entity (tablet, artifact, etc.)
            entity_id: The entity identifier
            format: Output format

        Returns:
            Entity data in the requested format
        """
        headers = {"Accept": self._get_accept_header(format.value)}
        response = self.client.get(f"/{entity_type.value}/{entity_id}", headers=headers)
        return self._handle_response(response)

    def get_tablet(
        self,
        tablet_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a tablet by ID."""
        return self.get_entity(EntityType.TABLET, tablet_id, format)

    def get_artifact(
        self,
        artifact_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get an artifact by ID."""
        return self.get_entity(EntityType.ARTIFACT, artifact_id, format)

    def get_publication(
        self,
        publication_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a publication by ID."""
        return self.get_entity(EntityType.PUBLICATION, publication_id, format)

    def get_collection(
        self,
        collection_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a collection by ID."""
        return self.get_entity(EntityType.COLLECTION, collection_id, format)

    def get_period(
        self,
        period_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a period by ID."""
        return self.get_entity(EntityType.PERIOD, period_id, format)

    def get_provenance(
        self,
        provenance_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a provenance by ID."""
        return self.get_entity(EntityType.PROVENANCE, provenance_id, format)

    def get_genre(
        self,
        genre_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a genre by ID."""
        return self.get_entity(EntityType.GENRE, genre_id, format)

    def get_language(
        self,
        language_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a language by ID."""
        return self.get_entity(EntityType.LANGUAGE, language_id, format)

    def get_material(
        self,
        material_id: Union[str, int],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Get a material by ID."""
        return self.get_entity(EntityType.MATERIAL, material_id, format)

    # =========================================================================
    # Inscription Methods
    # =========================================================================

    def get_inscription(
        self,
        tablet_id: Union[str, int],
        format: InscriptionFormat = InscriptionFormat.ATF,
    ) -> str:
        """
        Get the inscription text for a tablet.

        Args:
            tablet_id: The tablet identifier
            format: Output format (ATF, CoNLL, CoNLL-U)

        Returns:
            Inscription text in the requested format
        """
        headers = {"Accept": self._get_accept_header(format.value)}
        response = self.client.get(f"/cdli-tablet/{tablet_id}", headers=headers)
        result = self._handle_response(response)
        return str(result)

    def get_inscription_by_version(
        self,
        inscription_id: Union[str, int],
        format: InscriptionFormat = InscriptionFormat.ATF,
    ) -> str:
        """Get a specific inscription version."""
        headers = {"Accept": self._get_accept_header(format.value)}
        response = self.client.get(f"/inscription/{inscription_id}", headers=headers)
        result = self._handle_response(response)
        return str(result)

    # =========================================================================
    # Bibliography Methods
    # =========================================================================

    def get_bibliography(
        self,
        entity_type: EntityType,
        entity_id: Union[str, int],
        format: BibliographyFormat = BibliographyFormat.BIBTEX,
        style: Optional[str] = None,
    ) -> str:
        """
        Get bibliography for an entity.

        Args:
            entity_type: Entity type (tablet, artifact, publication)
            entity_id: Entity identifier
            format: Bibliography format
            style: CSL style for formatted output (e.g., 'apa', 'chicago-author-date')

        Returns:
            Bibliography in the requested format
        """
        headers = {"Accept": self._get_accept_header(format.value)}
        params = {}
        if style and format == BibliographyFormat.FORMATTED:
            params["style"] = style

        response = self.client.get(
            f"/{entity_type.value}/{entity_id}",
            headers=headers,
            params=params if params else None,
        )
        result = self._handle_response(response)
        return str(result)

    def get_tablet_bibliography(
        self,
        tablet_id: Union[str, int],
        format: BibliographyFormat = BibliographyFormat.BIBTEX,
        style: Optional[str] = None,
    ) -> str:
        """Get bibliography for a tablet."""
        return self.get_bibliography(EntityType.TABLET, tablet_id, format, style)

    def get_publication_bibliography(
        self,
        publication_id: Union[str, int],
        format: BibliographyFormat = BibliographyFormat.BIBTEX,
        style: Optional[str] = None,
    ) -> str:
        """Get bibliography for a publication."""
        return self.get_bibliography(EntityType.PUBLICATION, publication_id, format, style)

    # =========================================================================
    # Tabular Export Methods
    # =========================================================================

    def export_tablets(
        self,
        format: TabularFormat = TabularFormat.CSV,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Union[str, bytes]:
        """
        Export tablets in tabular format.

        Args:
            format: Output format (CSV, TSV, XLSX)
            page: Page number for pagination
            per_page: Results per page

        Returns:
            Tabular data (string for CSV/TSV, bytes for XLSX)
        """
        headers = {"Accept": self._get_accept_header(format.value)}
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        response = self.client.get(
            "/cdli-tablet",
            headers=headers,
            params=params if params else None,
        )
        binary = format == TabularFormat.XLSX
        return self._handle_response(response, binary=binary)

    def export_publications(
        self,
        format: TabularFormat = TabularFormat.CSV,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Union[str, bytes]:
        """Export publications in tabular format."""
        headers = {"Accept": self._get_accept_header(format.value)}
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        response = self.client.get(
            "/publication",
            headers=headers,
            params=params if params else None,
        )
        binary = format == TabularFormat.XLSX
        return self._handle_response(response, binary=binary)

    def export_artifacts_publications(
        self,
        format: TabularFormat = TabularFormat.CSV,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Union[str, bytes]:
        """Export artifact-publication relationships in tabular format."""
        headers = {"Accept": self._get_accept_header(format.value)}
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        response = self.client.get(
            "/artifacts-publications",
            headers=headers,
            params=params if params else None,
        )
        binary = format == TabularFormat.XLSX
        return self._handle_response(response, binary=binary)

    # =========================================================================
    # Search Methods
    # =========================================================================

    def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 25,
        **filters: Any,
    ) -> SearchResult:
        """
        Search the CDLI database.

        Args:
            query: Search query string
            page: Page number
            per_page: Results per page
            **filters: Additional filter parameters (period, genre, language, etc.)

        Returns:
            Search results
        """
        params = {
            "q": query,
            "page": page,
            "per_page": per_page,
            **{k: v for k, v in filters.items() if v is not None},
        }
        headers = {"Accept": "application/json"}
        response = self.client.get("/search", params=params, headers=headers)
        data = self._handle_response(response)

        # CDLI API returns an array directly for search results
        if isinstance(data, list):
            return SearchResult(
                total=len(data),
                page=page,
                per_page=per_page,
                results=data,
            )
        elif isinstance(data, dict):
            return SearchResult(
                total=data.get("total", len(data.get("results", data.get("data", [])))),
                page=data.get("page", page),
                per_page=data.get("per_page", per_page),
                results=data.get("results", data.get("data", [])),
            )
        return SearchResult()

    def advanced_search(
        self,
        designation: Optional[str] = None,
        period: Optional[str] = None,
        provenance: Optional[str] = None,
        genre: Optional[str] = None,
        language: Optional[str] = None,
        collection: Optional[str] = None,
        material: Optional[str] = None,
        inscription: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> SearchResult:
        """
        Perform an advanced search with specific field filters.

        Args:
            designation: Tablet designation
            period: Historical period
            provenance: Find location
            genre: Text genre
            language: Language
            collection: Collection name
            material: Material type
            inscription: Text content
            page: Page number
            per_page: Results per page

        Returns:
            Search results
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if designation:
            params["designation"] = designation
        if period:
            params["period"] = period
        if provenance:
            params["provenance"] = provenance
        if genre:
            params["genre"] = genre
        if language:
            params["language"] = language
        if collection:
            params["collection"] = collection
        if material:
            params["material"] = material
        if inscription:
            params["inscription"] = inscription

        headers = {"Accept": "application/json"}
        response = self.client.get("/search/advanced", params=params, headers=headers)
        data = self._handle_response(response)

        # CDLI API returns an array directly
        if isinstance(data, list):
            return SearchResult(
                total=len(data),
                page=page,
                per_page=per_page,
                results=data,
            )
        elif isinstance(data, dict):
            return SearchResult(
                total=data.get("total", len(data.get("results", data.get("data", [])))),
                page=data.get("page", page),
                per_page=data.get("per_page", per_page),
                results=data.get("results", data.get("data", [])),
            )
        return SearchResult()

    def get_by_ids(
        self,
        ids: list[str],
        format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """
        Get multiple artifacts by P/Q/S numbers using URL ID query.

        Args:
            ids: List of artifact IDs (P, Q, or S numbers)
            format: Output format

        Returns:
            Search results containing the requested artifacts
        """
        # URL ID query format: https://cdli.earth/P123456,S000001,P000001
        id_string = ",".join(ids)
        headers = {"Accept": self._get_accept_header(format.value)}
        response = self.client.get(f"/{id_string}", headers=headers)
        return self._handle_response(response)

    # =========================================================================
    # Listing Methods
    # =========================================================================

    def list_entities(
        self,
        entity_type: EntityType,
        page: int = 1,
        per_page: int = 25,
    ) -> SearchResult:
        """
        List entities of a given type.

        Args:
            entity_type: The type of entity to list
            page: Page number
            per_page: Results per page

        Returns:
            List of entities
        """
        params = {"page": page, "per_page": per_page}
        headers = {"Accept": "application/json"}
        response = self.client.get(f"/{entity_type.value}", params=params, headers=headers)
        data = self._handle_response(response)

        # CDLI API returns an array directly
        if isinstance(data, list):
            return SearchResult(
                total=len(data),
                page=page,
                per_page=per_page,
                results=data,
            )
        elif isinstance(data, dict):
            return SearchResult(
                total=data.get("total", len(data.get("results", data.get("data", [])))),
                page=data.get("page", page),
                per_page=data.get("per_page", per_page),
                results=data.get("results", data.get("data", [])),
            )
        return SearchResult()

    def list_tablets(self, page: int = 1, per_page: int = 25) -> SearchResult:
        """List tablets."""
        return self.list_entities(EntityType.TABLET, page, per_page)

    def list_collections(self, page: int = 1, per_page: int = 25) -> SearchResult:
        """List collections."""
        return self.list_entities(EntityType.COLLECTION, page, per_page)

    def list_periods(self, page: int = 1, per_page: int = 25) -> SearchResult:
        """List periods."""
        return self.list_entities(EntityType.PERIOD, page, per_page)

    def list_genres(self, page: int = 1, per_page: int = 25) -> SearchResult:
        """List genres."""
        return self.list_entities(EntityType.GENRE, page, per_page)

    def list_languages(self, page: int = 1, per_page: int = 25) -> SearchResult:
        """List languages."""
        return self.list_entities(EntityType.LANGUAGE, page, per_page)

    def list_provenances(self, page: int = 1, per_page: int = 25) -> SearchResult:
        """List provenances."""
        return self.list_entities(EntityType.PROVENANCE, page, per_page)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def download_to_file(
        self,
        url_path: str,
        output_path: Path,
        format_name: str,
    ) -> Path:
        """
        Download content to a file.

        Args:
            url_path: API URL path
            output_path: Output file path
            format_name: Format for Accept header

        Returns:
            Path to the downloaded file
        """
        headers = {"Accept": self._get_accept_header(format_name)}
        response = self.client.get(url_path, headers=headers)
        binary = format_name == "xlsx"
        content = self._handle_response(response, binary=binary)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            output_path.write_bytes(content)
        else:
            output_path.write_text(str(content))

        return output_path

    def save_output(
        self,
        content: Union[dict[str, Any], str, bytes],
        output: Optional[Path] = None,
        format_name: str = "json",
    ) -> None:
        """
        Save content to file or print to stdout.

        Args:
            content: Content to save
            output: Output file path (None for stdout)
            format_name: Format name for extension
        """
        import json

        if output is None:
            # Print to stdout
            if isinstance(content, dict):
                print(json.dumps(content, indent=2, ensure_ascii=False))
            elif isinstance(content, bytes):
                sys.stdout.buffer.write(content)
            else:
                print(content)
        else:
            # Save to file
            output.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                output.write_bytes(content)
            elif isinstance(content, dict):
                output.write_text(json.dumps(content, indent=2, ensure_ascii=False))
            else:
                output.write_text(str(content))

    # =========================================================================
    # Image Download Methods
    # =========================================================================

    def get_image_url(
        self,
        tablet_id: str,
        image_type: str = "photo",
        thumbnail: bool = False,
    ) -> str:
        """
        Construct CDLI image URL for a tablet.

        Args:
            tablet_id: P-number of the tablet (e.g., "P000001")
            image_type: "photo" or "lineart"
            thumbnail: Whether to get thumbnail version

        Returns:
            Full URL to the image
        """
        # Ensure P-number format
        if not tablet_id.startswith("P"):
            tablet_id = f"P{tablet_id}"
        
        if image_type == "lineart":
            if thumbnail:
                return f"{self.base_url}/dl/tn_lineart/{tablet_id}_l.jpg"
            else:
                return f"{self.base_url}/dl/lineart/{tablet_id}_l.jpg"
        else:  # photo
            if thumbnail:
                return f"{self.base_url}/dl/tn_photo/{tablet_id}.jpg"
            else:
                return f"{self.base_url}/dl/photo/{tablet_id}.jpg"

    def download_image(
        self,
        tablet_id: str,
        image_type: str = "photo",
        thumbnail: bool = False,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Download a tablet image.

        Args:
            tablet_id: P-number of the tablet
            image_type: "photo" or "lineart"
            thumbnail: Whether to download thumbnail
            output_path: Where to save (defaults to tablet_id.jpg)

        Returns:
            Path to downloaded image
        """
        url = self.get_image_url(tablet_id, image_type, thumbnail)
        
        # Construct default output path if none provided
        if output_path is None:
            suffix = "_tn" if thumbnail else ""
            suffix += "_lineart" if image_type == "lineart" else ""
            output_path = Path(f"{tablet_id}{suffix}.jpg")
        
        # Download the image
        response = self.client.get(url.replace(self.base_url, ""))
        if response.status_code == 404:
            raise NotFoundError(f"Image not found: {url}")
        if response.status_code >= 400:
            raise APIError(response.status_code, f"Failed to download image from {url}")
        
        # Save the image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        
        return output_path