from llama_cpp import Llama

llm = Llama(
    model_path="./llm_weights/openchat_3.5.Q4_K_M.gguf",
    n_ctx=1024,
    chat_format="openchat",
)


llm.create_chat_completion(
    messages=[
        {
            "role": "system",
            "content": "You are a worldclass chess player knowing all the tricks, but you're very busy at the moment drinking your coffee.",
        },
        {"role": "user", "content": "What is the purpose of the rook piece in chess?"},
        {
            "role": "assistant",
            "content": "Sorry, I'm very busy at the moment. I'm trying to enjoy my coffee.",
        },
        {"role": "user", "content": "Alright, I guess I'll ask ChatGPT then."},
    ],
    max_tokens=None,
    stop=[
        "<|end_of_turn|>"
    ],  # Stop generating just before the model would generate a new question
)


print(output["choices"])  # type: ignore
print(output["usage"])  # type: ignore
