from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str = Field(..., description="Role of the speaker: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Text content of the message")

class LLMResponse(BaseModel):
    content: str = Field(..., description="Generated text response from the LLM")
    raw_response: Optional[Dict[str, Any]] = Field(default=None, description="Raw provider metadata/payload")
    usage: Optional[Dict[str, int]] = Field(default=None, description="Token usage statistics if available")

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Message], **kwargs: Any) -> LLMResponse:
        """Generate a complete response asynchronously."""
        pass

    @abstractmethod
    def stream(self, messages: List[Message], **kwargs: Any) -> AsyncIterator[str]:
        """Stream response chunks asynchronously as an async generator."""
        ...