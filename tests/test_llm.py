import pytest
from mitsuki.llm.base import Message
from mitsuki.llm.ollama import OllamaProvider

@pytest.mark.asyncio
async def test_ollama_provider_generate(mocker):
    # Arrange
    mock_response_json = {
        "message": {
            "role": "assistant",
            "content": "Hello! I am Mitsuki, running locally on your hardware."
        },
        "done": True
    }

    # Create a mock response object
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_json
    mock_response.raise_for_status.return_value = None

    # Use AsyncMock for the async post method
    mock_client_post = mocker.AsyncMock(return_value=mock_response)
    mocker.patch("httpx.AsyncClient.post", mock_client_post)

    provider = OllamaProvider(model_name="llama3", base_url="http://localhost:11434")
    messages = [Message(role="user", content="Hi there!")]

    # Act
    result = await provider.generate(messages)

    # Assert
    assert result.content == "Hello! I am Mitsuki, running locally on your hardware."
    assert result.raw_response == mock_response_json
    mock_client_post.assert_awaited_once()