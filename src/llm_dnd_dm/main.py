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


def start_new_chat():

    memory = MessagesMemory()

    llm = setup_llm(
        "src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=1024,
        chat_format="openchat",
        verbose=False,
    )

    system_message = "You are a worldclass chess player knowing all the tricks, but you're very busy at the moment drinking your coffee and don't want to be disturbed by anyone."
    memory.create_system_prompt(system_message=system_message, session="test")

    run_chat_instance(memory=memory, llm=llm)


def continue_chat():

    memory = MessagesMemory()

    llm = setup_llm(
        ".llm_weights/openchat_3.5.04_K_M-gguf",
        n_ctx=102,
        chat_format="openchat",
        verbose=False,
    )

    run_chat_instance(memory=memory, llm=llm)


def run_chat_instance(memory: MessagesMemory, llm: Llama):

    while True:

        user_message = input("What would you like to tell the chatbot?\n")

        prompt = memory.create_user_prompt(
            user_message=user_message,
            session="test",
        )

        output = llm.create_chat_completion(
            messages=prompt,
            max_tokens=None,
            stop=[
                "<|end_of_turn|>"
            ],  # Stop generating just before the model would generate a new question
        )

        print(output["choices"])  # type: ignore
        print(output["usage"])  # type: ignore

        chat_answer = output["choices"][0]["message"]  # type: ignore

        memory.save_messages_on_disk(chat_answer, session="test", new_chat=False)


start_new_chat()
