import httpx
import ollama

from src.config import settings


class LLMError(Exception):
    """Raised when the LLM can't produce a reply (Ollama down, model missing, etc.)."""


def ask(messages: list[dict]) -> str:
    """Send a chat history to Ollama and return the assistant's reply text.

    Each message is {"role": "system" | "user" | "assistant", "content": str}.
    Raises LLMError with a human-readable hint if Ollama is unreachable or the model is missing.
    """
    client = ollama.Client(host=settings.ollama_url)
    try:
        response = client.chat(model=settings.ollama_model, messages=messages)
    except (ConnectionError, httpx.ConnectError) as e:
        raise LLMError(
            f"Can't reach Ollama at {settings.ollama_url}. Is it running? Try: ollama serve"
        ) from e
    except httpx.TransportError as e:
        # Connected, then the server dropped or stalled (e.g. model failed to load, runner crashed).
        raise LLMError(
            f"Ollama at {settings.ollama_url} dropped the request ({type(e).__name__}). "
            f"The model '{settings.ollama_model}' may have failed to load; "
            "check the `ollama serve` log and try: ollama run " + settings.ollama_model
        ) from e
    except ollama.ResponseError as e:
        if e.status_code == 404:
            raise LLMError(
                f"Model '{settings.ollama_model}' not found. "
                f"Run: ollama pull {settings.ollama_model}"
            ) from e
        raise LLMError(f"Ollama error: {e.error}") from e
    return response["message"]["content"]
