"""
Tests for Redfish Client

Unit tests for the RedfishClient class.
"""

import pytest
from unittest.mock import Mock, patch
from core.redfish_client import RedfishClient


@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    with patch('core.redfish_client.requests.Session') as mock:
        yield mock


def test_client_initialization():
    """Test RedfishClient initialization."""
    client = RedfishClient(
        host="test.example.com",
        username="admin",
        password="password"
    )

    assert client.host == "test.example.com"
    assert client.username == "admin"
    assert client.port == 443
    assert client.base_url == "https://test.example.com:443"


def test_client_custom_port():
    """Test RedfishClient with custom port."""
    client = RedfishClient(
        host="test.example.com",
        username="admin",
        password="password",
        port=8443
    )

    assert client.port == 8443
    assert client.base_url == "https://test.example.com:8443"


# Add more tests here
# TODO: Add tests for get(), get_systems(), get_thermal(), etc.
