import pytest
from src.llama_interaction import load_llama_model, get_llama_result

@pytest.fixture
def mock_llama(mocker):
    return mocker.patch('src.llama_interaction.Llama', return_value='llama_model')

@pytest.fixture
def mock_download(mocker):
    return mocker.patch('src.llama_interaction.hf_hub_download', return_value='model_path')

def test_load_llama_model(mock_download, mock_llama):
    result = load_llama_model()
    mock_download.assert_called_with(repo_id="TheBloke/Llama-2-13B-chat-GGML", filename="llama-2-13b-chat.ggmlv3.q5_1.bin")
    mock_llama.assert_called_with(model_path='model_path', n_threads=2, n_batch=512, n_gpu_layers=32)
    assert result == 'llama_model'

@pytest.mark.parametrize("prompt, expected_result", [
    ("prompt1", "test_response1"),
    ("prompt2", "test_response2"),
    ("prompt3", "test_response3"),
])
def test_get_llama_result(mock_llama, prompt, expected_result):
    mock_llama.return_value = {"choices": [{"text": expected_result}]}
    result = get_llama_result(mock_llama, prompt)
    mock_llama.assert_called_with(prompt=prompt, max_tokens=256, temperature=0.5, top_p=0.95, repeat_penalty=1.2, top_k=150, echo=True)
    assert result == expected_result

def test_get_llama_result_exception(mock_llama):
    mock_llama.side_effect = Exception("test_exception")
    result = get_llama_result(mock_llama, "prompt")
    assert result == "Error during interaction: test_exception"