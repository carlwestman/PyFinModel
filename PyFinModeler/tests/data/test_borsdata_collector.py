import pytest
import os
import json
from unittest.mock import patch, MagicMock
from PyFinModeler.data.borsdata_collector import BorsdataCollector
from PyFinModeler.core.company import Company

# Get the absolute path to the `mock_data` directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DATA_DIR = os.path.join(BASE_DIR, "mock_data")


def test_borsdata_collector_initialization():
    """Test initialization of the BorsdataCollector."""
    collector = BorsdataCollector(api_key="test_key")
    assert collector.api_key == "test_key"
    assert collector.BASE_URL == "https://apiservice.borsdata.se/v1"


@patch("requests.Session.get")
def test_get_all_companies(mock_get):
    """Test fetching all companies from Börsdata."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    with open(os.path.join(MOCK_DATA_DIR, "mock_instruments.json"), "r") as f:
        mock_response.json.return_value = {"instruments": json.load(f)["instruments"]}
    mock_get.return_value = mock_response

    collector = BorsdataCollector(api_key="test_key")
    companies = collector.get_all_companies()

    assert len(companies) == 2
    assert companies[0]["name"] == "Company A"
    assert companies[1]["ticker"] == "COMPB"
    mock_get.assert_called_once_with(
        f"{collector.BASE_URL}/instruments", params={"authKey": "test_key"}
    )


@patch("requests.Session.get")
def test_fetch_company_by_name(mock_get):
    """Test fetching a company by name."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    with open(os.path.join(MOCK_DATA_DIR, "mock_instruments.json"), "r") as f:
        mock_response.json.return_value = {"instruments": json.load(f)["instruments"]}
    mock_get.return_value = mock_response

    collector = BorsdataCollector(api_key="test_key")
    company = collector.fetch_company(name="Company A")

    assert company.name == "Company A"
    assert company.ticker == "COMPA"
    assert company.currency == "SEK"
    assert collector.current_company_id == 101  # Check the company_id on the collector


@patch("requests.Session.get")
def test_fetch_company_by_name_no_match(mock_get):
    """Test fetching a company by name with no match."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    with open(os.path.join(MOCK_DATA_DIR, "mock_instruments.json"), "r") as f:
        mock_response.json.return_value = {"instruments": json.load(f)["instruments"]}
    mock_get.return_value = mock_response

    collector = BorsdataCollector(api_key="test_key")
    company = collector.fetch_company(name="NonExistentCompany")

    assert company is None


@patch("requests.Session.get")
def test_get_reports(mock_get):
    """Test fetching reports for a company."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    with open(os.path.join(MOCK_DATA_DIR, "mock_instrument_report.json"), "r") as f:
        mock_response.json.return_value = json.load(f)
    mock_get.return_value = mock_response

    collector = BorsdataCollector(api_key="test_key")
    reports = collector._get_reports(company_id=101, report_type="year", max_count=2)

    assert len(reports) == 2
    assert reports[0]["year"] == 2022
    assert reports[1]["revenues"] == 1100000.0
    mock_get.assert_called_once_with(
        f"{collector.BASE_URL}/instruments/101/reports/year",
        params={"authKey": "test_key", "maxCount": 2, "original": 0},
    )


@patch("requests.Session.get")
def test_get_all_companies_failure(mock_get):
    """Test handling of failure when fetching all companies."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"message": "Internal Server Error"}
    mock_get.return_value = mock_response

    collector = BorsdataCollector(api_key="test_key")
    with pytest.raises(Exception, match="500 Server Error"):
        collector.get_all_companies()