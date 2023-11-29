from llama_cpp import Llama
from huggingface_hub import hf_hub_download


def load_llama_model() -> Llama:
    model_name_or_path: str = "TheBloke/Llama-2-13B-chat-GGML"
    model_basename: str = "llama-2-13b-chat.ggmlv3.q5_1.bin"
    model_path: str = hf_hub_download(repo_id=model_name_or_path, filename=model_basename)
    lcpp_llm: Llama = Llama(model_path=model_path, n_threads=2, n_batch=512, n_gpu_layers=32)
    return lcpp_llm


def get_llama_result(lcpp_llm: Llama, prompt: str) -> str:
    try:
        response: dict = lcpp_llm(prompt=prompt, max_tokens=256, temperature=0.5, top_p=0.95, repeat_penalty=1.2,
                                  top_k=150, echo=True)
        result_text: str = response["choices"][0]["text"]
    except Exception as e:
        result_text = f"Error during interaction: {str(e)}"

    return result_text