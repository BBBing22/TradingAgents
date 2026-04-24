import os

from tradingagents.llm_clients import create_llm_client


def main() -> None:
    base_url = os.getenv("TRADINGAGENTS_BACKEND_URL", "http://localhost:11434/v1")
    model = os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", "tinyllama:1.1b")

    client = create_llm_client(
        provider="ollama",
        model=model,
        base_url=base_url,
        timeout=60,
        max_retries=1,
    )
    llm = client.get_llm()

    resp = llm.invoke("Reply with a short message.")
    text = getattr(resp, "content", None) if hasattr(resp, "content") else str(resp)

    if not text or not str(text).strip():
        raise SystemExit("Empty response")

    print("OK")


if __name__ == "__main__":
    main()
