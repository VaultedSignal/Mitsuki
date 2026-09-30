import os
from pydantic_settings import BaseSettings

class LLMSettings(BaseSettings):
    provider: str = os.getenv("MITSUKI_LLM_PROVIDER", "ollama")
    model_name: str = os.getenv("MITSUKI_LLM_MODEL", "qwen3:8b")
    base_url: str = os.getenv("MITSUKI_LLM_BASE_URL", "http://localhost:11434")
    temperature: float = float(os.getenv("MITSUKI_LLM_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("MITSUKI_LLM_MAX_TOKENS", "2048"))
    timeout: float = float(os.getenv("MITSUKI_LLM_TIMEOUT", "60.0"))

    class Config:
        env_prefix = "MITSUKI_LLM_"
        case_insensitive = True

llm_settings = LLMSettings()