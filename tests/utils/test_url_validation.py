import pytest

from app.utils.url_validation import (
    is_loopback_host,
    validate_https_or_loopback_http_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://example.com/healthz",
        "https://example.com:8443/api/v1",
        "https://user:password@example.com/private",
    ],
)
def test_validate_https_or_loopback_http_url_accepts_https_urls(url: str):
    assert validate_https_or_loopback_http_url(url, service_name="Test Service") == url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "http://localhost:3000/callback",
        "http://127.0.0.1:8080/api",
        "http://[::1]:9090/metrics",
        "http://user:password@localhost:8000/private",
    ],
)
def test_validate_https_or_loopback_http_url_accepts_loopback_http_urls(url: str):
    assert validate_https_or_loopback_http_url(url, service_name="Test Service") == url


def test_validate_https_or_loopback_http_url_returns_empty_for_empty_url():
    assert validate_https_or_loopback_http_url("", service_name="Test Service") == ""


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "example.com/path",
        "not a url",
        "https:///missing-host",
        "ftp://example.com",
    ],
)
def test_validate_https_or_loopback_http_url_rejects_invalid_urls(url: str):
    with pytest.raises(
        ValueError,
        match="Test Service base_url must use https:// unless targeting localhost/loopback.",
    ):
        validate_https_or_loopback_http_url(url, service_name="Test Service")


def test_validate_https_or_loopback_http_url_uses_custom_field_name_in_error():
    with pytest.raises(
        ValueError,
        match="Test Service webhook_url must use https:// unless targeting localhost/loopback.",
    ):
        validate_https_or_loopback_http_url(
            "http://example.com",
            service_name="Test Service",
            field_name="webhook_url",
        )


@pytest.mark.parametrize(
    "host",
    [
        "localhost",
        " LOCALHOST ",
        "127.0.0.1",
        "127.255.255.255",
        "::1",
        "[::1]",
    ],
)
def test_is_loopback_host_returns_true_for_localhost_and_loopback_ips(host: str):
    assert is_loopback_host(host) is True


@pytest.mark.parametrize(
    "host",
    [
        "example.com",
        "10.0.0.1",
        "192.168.1.10",
        "8.8.8.8",
        "",
        "localhost.example.com",
    ],
)
def test_is_loopback_host_returns_false_for_non_loopback_hosts(host: str):
    assert is_loopback_host(host) is False


def test_is_loopback_host_returns_false_for_host_port_string():
    # 127.0.0.1 is loopback, but is_loopback_host expects a bare host;
    # ip_address() raises ValueError on "host:port" input so False is returned.
    assert is_loopback_host("127.0.0.1:8080") is False
