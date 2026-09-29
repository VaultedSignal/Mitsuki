# Local Ollama provider implementation
import json
from typing import Any, AsyncIterator, List
import httpx
from .base import BaseLLMProvider, Message, LLMResponse

class OllamaProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434", timeout: float = 60.0):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048),
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            content = data.get("message", {}).get("content", "")
            return LLMResponse(content=content, raw_response=data)

    async def stream(self, messages: List[Message], **kwargs: Any) -> AsyncIterator[str]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048),
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk