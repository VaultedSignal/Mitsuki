from typing import List, Optional
from mitsuki.llm.base import Message
from mitsuki.memory.database import MemoryManager

class ConversationManager:
    """Manages chat conversation history, persistent SQLite storage, and dynamic fact injection."""
    
    def __init__(self, system_prompt: Optional[str] = None, max_history_messages: int = 20):
        self.base_system_prompt = system_prompt or ""
        self.max_history_messages = max_history_messages
        self.memory = MemoryManager()
        
        # Load past conversation history from SQLite on startup
        loaded_history = self.memory.load_history(limit=max_history_messages)
        self._messages: List[Message] = [
            Message(role=msg["role"], content=msg["content"]) for msg in loaded_history
        ]
        
    def _build_dynamic_system_prompt(self) -> str:
        """Injects persistent long-term facts into the base system prompt."""
        facts = self.memory.get_all_facts()
        if not facts:
            return self.base_system_prompt
            
        facts_block = "\n[KNOWN USER & RELATIONSHIP FACTS]\n"
        for key, value in facts.items():
            facts_block += f"- {key}: {value}\n"
            
        return self.base_system_prompt + "\n" + facts_block

    def add_message(self, role: str, content: str) -> None:
        """Append a new user or assistant turn to history and persist it."""
        self._messages.append(Message(role=role, content=content))
        self.memory.save_message(role=role, content=content)

    def remember_fact(self, key: str, value: str) -> None:
        """Manually or programmatically store a persistent fact."""
        self.memory.set_fact(key, value)

    async def extract_and_store_facts(self, llm_provider, user_input: str, assistant_response: str) -> None:
        """Passively analyze the latest exchange and extract persistent user facts."""
        extraction_prompt = [
            Message(
                role="system",
                content=(
                    "You are a background fact extractor. Analyze the latest user message and assistant response. "
                    "If the user shared a distinct personal fact, preference, hobby, or project, output it as 'KEY: VALUE'. "
                    "If no new durable fact is present, output 'NONE'. Keep keys concise (e.g., 'favorite_anime', 'current_project')."
                )
            ),
            Message(role="user", content=f"User: {user_input}\nAssistant: {assistant_response}")
        ]
        
        try:
            response = await llm_provider.generate(extraction_prompt)
            content = response.content.strip()
            
            if ":" in content and "NONE" not in content.upper():
                parts = content.split(":", 1)
                key = parts[0].strip().lower().replace(" ", "_")
                value = parts[1].strip()
                if key and value:
                    self.remember_fact(key, value)
        except Exception:
            # Fail silently in the background so chat latency is never impacted
            pass

    def get_messages(self) -> List[Message]:
        """Constructs the full payload combining the dynamic system prompt and recent history."""
        payload: List[Message] = []
        
        # Build system prompt with current long-term facts injected
        current_system_prompt = self._build_dynamic_system_prompt()
        if current_system_prompt:
            payload.append(Message(role="system", content=current_system_prompt))
            
        if self.max_history_messages > 0 and len(self._messages) > self.max_history_messages:
            history_window = self._messages[-self.max_history_messages:]
        else:
            history_window = self._messages
            
        payload.extend(history_window)
        return payload

    def clear(self) -> None:
        """Clear message history while retaining long-term facts."""
        self._messages.clear()
        self.memory.clear_history()