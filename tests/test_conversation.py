import pytest
from mitsuki.core.conversation import ConversationManager

def test_conversation_manager_initialization():
    manager = ConversationManager(system_prompt="You are Mitsuki.")
    assert manager.system_prompt == "You are Mitsuki."
    
    messages = manager.get_messages()
    assert len(messages) == 1
    assert messages[0].role == "system"
    assert messages[0].content == "You are Mitsuki."

def test_add_and_retrieve_messages():
    manager = ConversationManager(system_prompt="You are a helpful companion.")
    manager.add_message("user", "Hello Mitsuki!")
    manager.add_message("assistant", "Hello! How can I help you today?")
    
    messages = manager.get_messages()
    assert len(messages) == 3
    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert messages[1].content == "Hello Mitsuki!"
    assert messages[2].role == "assistant"
    assert messages[2].content == "Hello! How can I help you today?"

def test_history_truncation_limit():
    # Limit history to 2 messages
    manager = ConversationManager(max_history_messages=2)
    manager.add_message("user", "Message 1")
    manager.add_message("assistant", "Message 2")
    manager.add_message("user", "Message 3")
    
    messages = manager.get_messages()
    # Should only contain the last 2 messages
    assert len(messages) == 2
    assert messages[0].content == "Message 2"
    assert messages[1].content == "Message 3"