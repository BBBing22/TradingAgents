import importlib
import os


def test_yfinance_proxy_env_precedence(monkeypatch):
    monkeypatch.delenv("TRADINGAGENTS_YFINANCE_PROXY", raising=False)
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)

    monkeypatch.setenv("HTTP_PROXY", "http://proxy-http:7890")
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy-https:7890")

    import tradingagents.dataflows.stockstats_utils as su
    importlib.reload(su)

    assert su.get_yfinance_proxy() == "http://proxy-https:7890"

    monkeypatch.setenv("TRADINGAGENTS_YFINANCE_PROXY", "socks5h://local:7890")
    importlib.reload(su)

    assert su.get_yfinance_proxy() == "socks5h://local:7890"


def test_yfinance_session_includes_proxy(monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_YFINANCE_PROXY", "http://proxy:7890")

    import tradingagents.dataflows.stockstats_utils as su
    importlib.reload(su)

    session = su.get_yfinance_session()
    assert session.proxies.get("http") == "http://proxy:7890"
    assert session.proxies.get("https") == "http://proxy:7890"


def test_yfinance_session_is_curl_cffi(monkeypatch):
    monkeypatch.delenv("TRADINGAGENTS_YFINANCE_PROXY", raising=False)

    import tradingagents.dataflows.stockstats_utils as su
    importlib.reload(su)

    session = su.get_yfinance_session()
    assert session.__class__.__module__.startswith("curl_cffi")
