from llama_cpp import Llama
from memory import SummaryMemory

llm = Llama(model_path="./llm_weights/openchat_3.5.Q4_K_M.gguf", n_ctx=1024)

chess_prompt = "You are a worldclass chess player knowing all the tricks.<|end_of_turn|>GPT4 Correct User: What is the purpose of the rook piece in chess?<|end_of_turn|>GPT4 Correct Assistant:"

"""
output = llm(
    chess_prompt,  # Prompt
    max_tokens=None,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
    stop=[
        "<|end_of_turn|>"
    ],  # Stop generating just before the model would generate a new question
)  # Generate a completion, can also call create_completion
"""

output = llm.create_completion(
    chess_prompt,  # Prompt
    max_tokens=None,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
    stop=[
        "<|end_of_turn|>"
    ],  # Stop generating just before the model would generate a new question
)


print(output["choices"])  # type: ignore
print(output["usage"])  # type: ignore
