import importlib
import os


def test_default_config_env_override():
    keys = (
        "TRADINGAGENTS_LLM_PROVIDER",
        "TRADINGAGENTS_BACKEND_URL",
        "TRADINGAGENTS_QUICK_THINK_LLM",
        "TRADINGAGENTS_DEEP_THINK_LLM",
    )
    old = {k: os.environ.get(k) for k in keys}

    os.environ["TRADINGAGENTS_LLM_PROVIDER"] = "ollama"
    os.environ["TRADINGAGENTS_BACKEND_URL"] = "http://localhost:11434/v1"
    os.environ["TRADINGAGENTS_QUICK_THINK_LLM"] = "tinyllama:1.1b"
    os.environ["TRADINGAGENTS_DEEP_THINK_LLM"] = "tinyllama:1.1b"

    import tradingagents.default_config as dc
    importlib.reload(dc)

    assert dc.DEFAULT_CONFIG["llm_provider"] == "ollama"
    assert dc.DEFAULT_CONFIG["backend_url"] == "http://localhost:11434/v1"
    assert dc.DEFAULT_CONFIG["quick_think_llm"] == "tinyllama:1.1b"
    assert dc.DEFAULT_CONFIG["deep_think_llm"] == "tinyllama:1.1b"

    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
