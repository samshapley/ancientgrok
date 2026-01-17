"""Tests for the CDLI API client."""

import pytest
from pytest_httpx import HTTPXMock

from cdli_cli.client import CDLIClient
from cdli_cli.models import (
    BibliographyFormat,
    EntityType,
    InscriptionFormat,
    NotFoundError,
    OutputFormat,
    TabularFormat,
)


@pytest.fixture
def client():
    """Create a test client."""
    return CDLIClient()


def test_client_initialization():
    """Test client initialization."""
    client = CDLIClient()
    assert client.base_url == "https://cdli.earth"
    assert client.timeout == 30.0


def test_client_custom_base_url():
    """Test client with custom base URL."""
    client = CDLIClient(base_url="https://test.example.com")
    assert client.base_url == "https://test.example.com"


def test_client_context_manager(httpx_mock: HTTPXMock):
    """Test client context manager."""
    httpx_mock.add_response(
        url="https://cdli.earth/cdli-tablet/P000001",
        json={"id": 1, "designation": "Test Tablet"},
    )
    
    with CDLIClient() as client:
        result = client.get_tablet("P000001")
        assert result["designation"] == "Test Tablet"


def test_get_tablet(httpx_mock: HTTPXMock, client):
    """Test getting a tablet."""
    expected = {"id": 1, "designation": "Test Tablet", "period": "Ur III"}
    httpx_mock.add_response(
        url="https://cdli.earth/cdli-tablet/P000001",
        json=expected,
    )
    
    result = client.get_tablet("P000001")
    assert result == expected


def test_get_tablet_not_found(httpx_mock: HTTPXMock, client):
    """Test 404 error handling."""
    httpx_mock.add_response(
        url="https://cdli.earth/cdli-tablet/INVALID",
        status_code=404,
    )
    
    with pytest.raises(NotFoundError):
        client.get_tablet("INVALID")


def test_get_inscription_atf(httpx_mock: HTTPXMock, client):
    """Test getting inscription in ATF format."""
    expected_atf = "&P000001 = Test\n#atf: lang sux\n1. lu2 gal"
    httpx_mock.add_response(
        url="https://cdli.earth/cdli-tablet/P000001",
        text=expected_atf,
        headers={"content-type": "text/x-c-atf"},
    )
    
    result = client.get_inscription("P000001", InscriptionFormat.ATF)
    assert result == expected_atf


def test_search(httpx_mock: HTTPXMock, client):
    """Test search functionality."""
    expected = [
        {"id": 1, "designation": "Tablet 1"},
        {"id": 2, "designation": "Tablet 2"},
    ]
    httpx_mock.add_response(
        url="https://cdli.earth/search?q=test&page=1&per_page=25",
        json=expected,
    )
    
    result = client.search("test")
    assert result.total == 2
    assert len(result.results) == 2
    assert result.results[0]["designation"] == "Tablet 1"


def test_advanced_search(httpx_mock: HTTPXMock, client):
    """Test advanced search with filters."""
    expected = [{"id": 1, "period": "Ur III", "language": "Sumerian"}]
    httpx_mock.add_response(
        url="https://cdli.earth/search/advanced?page=1&per_page=25&period=Ur+III&language=Sumerian",
        json=expected,
    )
    
    result = client.advanced_search(period="Ur III", language="Sumerian")
    assert result.total == 1
    assert result.results[0]["period"] == "Ur III"


def test_export_tablets_csv(httpx_mock: HTTPXMock, client):
    """Test tablet export in CSV format."""
    csv_data = "id,designation,period\n1,Test,Ur III"
    httpx_mock.add_response(
        text=csv_data,
        headers={"content-type": "text/csv"},
    )
    
    result = client.export_tablets(TabularFormat.CSV)
    assert "Test" in result
    assert "Ur III" in result


def test_export_tablets_xlsx(httpx_mock: HTTPXMock, client):
    """Test tablet export in XLSX format."""
    xlsx_data = b"PK\x03\x04..."  # Mock Excel data
    httpx_mock.add_response(
        content=xlsx_data,
        headers={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    )
    
    result = client.export_tablets(TabularFormat.XLSX)
    assert isinstance(result, bytes)


def test_get_bibliography_bibtex(httpx_mock: HTTPXMock, client):
    """Test getting bibliography in BibTeX format."""
    bibtex_data = "@article{test2024,\n  title={Test},\n  year={2024}\n}"
    httpx_mock.add_response(
        url="https://cdli.earth/cdli-tablet/P000001",
        text=bibtex_data,
        headers={"content-type": "application/x-bibtex"},
    )
    
    result = client.get_tablet_bibliography("P000001", BibliographyFormat.BIBTEX)
    assert "@article" in result


def test_get_by_ids(httpx_mock: HTTPXMock, client):
    """Test URL ID query for multiple artifacts."""
    expected = [
        {"id": 1, "designation": "P000001"},
        {"id": 2, "designation": "S000001"},
    ]
    httpx_mock.add_response(
        url="https://cdli.earth/P000001,S000001",
        json=expected,
    )
    
    result = client.get_by_ids(["P000001", "S000001"])
    assert isinstance(result, list)
    assert len(result) == 2


def test_list_tablets(httpx_mock: HTTPXMock, client):
    """Test listing tablets."""
    expected = [
        {"id": 1, "designation": "Tablet 1"},
        {"id": 2, "designation": "Tablet 2"},
    ]
    httpx_mock.add_response(
        url="https://cdli.earth/cdli-tablet?page=1&per_page=25",
        json=expected,
    )
    
    result = client.list_tablets()
    assert result.total == 2
    assert len(result.results) == 2


def test_format_mime_types():
    """Test MIME type mappings exist for all formats."""
    from cdli_cli.models import FORMAT_MIME_TYPES
    
    assert "json" in FORMAT_MIME_TYPES
    assert "atf" in FORMAT_MIME_TYPES
    assert "bibtex" in FORMAT_MIME_TYPES
    assert "csv" in FORMAT_MIME_TYPES


def test_headers_include_accept(httpx_mock: HTTPXMock, client):
    """Test that search includes Accept header."""
    httpx_mock.add_response(
        url="https://cdli.earth/search?q=test&page=1&per_page=25",
        json=[],
    )
    
    client.search("test")
    
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers.get("Accept") == "application/json"


def test_get_image_url_photo(client):
    """Test image URL construction for photos."""
    url = client.get_image_url("P000001", "photo", False)
    assert url == "https://cdli.earth/dl/photo/P000001.jpg"


def test_get_image_url_photo_thumbnail(client):
    """Test image URL construction for photo thumbnails."""
    url = client.get_image_url("P000001", "photo", True)
    assert url == "https://cdli.earth/dl/tn_photo/P000001.jpg"


def test_get_image_url_lineart(client):
    """Test image URL construction for lineart."""
    url = client.get_image_url("P000001", "lineart", False)
    assert url == "https://cdli.earth/dl/lineart/P000001_l.jpg"


def test_get_image_url_lineart_thumbnail(client):
    """Test image URL construction for lineart thumbnails."""
    url = client.get_image_url("P000001", "lineart", True)
    assert url == "https://cdli.earth/dl/tn_lineart/P000001_l.jpg"


def test_get_image_url_adds_p_prefix(client):
    """Test that P prefix is added automatically."""
    url = client.get_image_url("000001", "photo")
    assert url == "https://cdli.earth/dl/photo/P000001.jpg"


def test_download_image(httpx_mock: HTTPXMock, client, tmp_path):
    """Test image download."""
    fake_image = b"\xff\xd8\xff\xe0"  # JPEG magic bytes
    httpx_mock.add_response(
        url="https://cdli.earth/dl/photo/P000001.jpg",
        content=fake_image,
        headers={"content-type": "image/jpeg"},
    )
    
    output = tmp_path / "test_image.jpg"
    result = client.download_image("P000001", "photo", output_path=output)
    
    assert result == output
    assert output.exists()
    assert output.read_bytes() == fake_image


def test_download_image_not_found(httpx_mock: HTTPXMock, client):
    """Test image download 404 handling."""
    httpx_mock.add_response(
        url="https://cdli.earth/dl/photo/PINVALID.jpg",
        status_code=404,
    )
    
    with pytest.raises(NotFoundError):
        client.download_image("INVALID", "photo")