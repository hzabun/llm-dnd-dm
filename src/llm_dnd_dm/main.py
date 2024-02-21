from llama_cpp import Llama
from memory import MessagesMemory
from typing import Any


def setup_llm(
    model_path: str, n_ctx: int, chat_format: str, verbose: bool = False
) -> Any:

    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        chat_format=chat_format,
        verbose=verbose,
    )
    return llm


def start_chat():

    memory = MessagesMemory()
    prompt_from_scratch = memory.create_new_chat_prompt(
        system_message="You are a worldclass chess player knowing all the tricks, but you're very busy at the moment drinking your coffee and don't want to be disturbed by anyone.",
        user_message="What is the purpose of the rook piece in chess?",
        session="test",
    )

    llm = setup_llm(
        ".llm_weights/openchat_3.5.04_K_M-gguf",
        n_ctx=102,
        chat_format="openchat",
        verbose=False,
    )

    output = llm.create_chat_completion(
        messages=prompt_from_scratch,
        max_tokens=None,
        stop=[
            "<|end_of_turn|>"
        ],  # Stop generating just before the model would generate a new question
    )

    print(output["choices"])  # type: ignore
    print(output["usage"])  # type: ignore

    chat_answer = output["choices"][0]["text"]  # type: ignore

    memory.save_messages_on_disk(chat_answer, session="test", new_chat=True)


def continue_chat():

    memory = MessagesMemory()
    prompt_with_history = memory.create_prompt_with_history(
        user_message="Alright, I guess I'll ask ChatGPT then if you're too busy with your coffee.",
        session="test",
    )

    llm = setup_llm(
        ".llm_weights/openchat_3.5.04_K_M-gguf",
        n_ctx=102,
        chat_format="openchat",
        verbose=False,
    )

    output = llm.create_chat_completion(
        messages=prompt_with_history,
        max_tokens=None,
        stop=[
            "<|end_of_turn|>"
        ],  # Stop generating just before the model would generate a new question
    )

    print(output["choices"])  # type: ignore
    print(output["usage"])  # type: ignore

    chat_answer = output["choices"][0]["text"]  # type: ignore

    memory.save_messages_on_disk(chat_answer, session="test", new_chat=False)
