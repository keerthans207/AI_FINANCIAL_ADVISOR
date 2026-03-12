from llama_cpp import Llama

llm = Llama(
    model_path="models/Phi-3-mini-4k-instruct-q4.gguf",
    n_ctx=2048,
    n_threads=4
)

response = llm("Explain budgeting in simple words.", max_tokens=100)
print(response["choices"][0]["text"])
