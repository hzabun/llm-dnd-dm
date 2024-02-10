from llama_cpp import Llama
from memory import MessagesMemory

llm = Llama(
    model_path="./llm_weights/openchat_3.5.Q4_K_M.gguf",
    n_ctx=1024,
    chat_format="openchat",
    verbose=False,
)
memory = MessagesMemory()

output = llm.create_chat_completion(
    messages=memory.load_messages(),
    max_tokens=None,
    stop=[
        "<|end_of_turn|>"
    ],  # Stop generating just before the model would generate a new question
)


print(output["choices"])  # type: ignore
print(output["usage"])  # type: ignore
