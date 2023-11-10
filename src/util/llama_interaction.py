from llama_cpp import Llama
from huggingface_hub import hf_hub_download


def load_llama_model():
    model_name_or_path = "TheBloke/Llama-2-13B-chat-GGML"
    model_basename = "llama-2-13b-chat.ggmlv3.q5_1.bin"
    model_path = hf_hub_download(repo_id=model_name_or_path, filename=model_basename)
    lcpp_llm = Llama(model_path=model_path, n_threads=2, n_batch=512, n_gpu_layers=32)
    return lcpp_llm


def get_llama_result(lcpp_llm, prompt):
    response = lcpp_llm(prompt=prompt, max_tokens=256, temperature=0.5, top_p=0.95, repeat_penalty=1.2,
                        top_k=150, echo=True)
    return response["choices"][0]["text"]