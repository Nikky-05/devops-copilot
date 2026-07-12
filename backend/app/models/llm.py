from functools import lru_cache

from langchain_core.language_models import BaseChatModel

from app.utils.config import get_settings


@lru_cache(maxsize=1)
def get_chat_llm() -> BaseChatModel:
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.anthropic_model,
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=8192,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER: {settings.llm_provider!r}. Use 'anthropic' or 'ollama'."
    )
