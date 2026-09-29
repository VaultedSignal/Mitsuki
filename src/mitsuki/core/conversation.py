from typing import List, Optional
from mitsuki.llm.base import Message

class ConversationManager:
    """Manages chat conversation history, system prompt injection, and context window trimming."""
    
    def __init__(self, system_prompt: Optional[str] = None, max_history_messages: int = 20):
        self.system_prompt = system_prompt
        self.max_history_messages = max_history_messages
        self._messages: List[Message] = []
        
    def set_system_prompt(self, prompt: str) -> None:
        """Update or set the persistent system prompt."""
        self.system_prompt = prompt

    def add_message(self, role: str, content: str) -> None:
        """Append a new user or assistant turn to the history buffer."""
        self._messages.append(Message(role=role, content=content))

    def get_messages(self) -> List[Message]:
        """Constructs the full payload for the LLM combining system prompt and recent history."""
        payload: List[Message] = []
        
        if self.system_prompt:
            payload.append(Message(role="system", content=self.system_prompt))
            
        if self.max_history_messages > 0 and len(self._messages) > self.max_history_messages:
            history_window = self._messages[-self.max_history_messages:]
        else:
            history_window = self._messages
            
        payload.extend(history_window)
        return payload

    def clear(self) -> None:
        """Clear all chat turns while retaining the system prompt."""
        self._messages.clear()