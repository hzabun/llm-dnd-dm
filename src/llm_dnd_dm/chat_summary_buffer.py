from llama_cpp import Llama
from memory import SummaryBufferMemory
from typing import Optional


def start_summary_buffer_chat(session: str) -> None:

    system_message = "The AI assistant is a worldclass chess player knowing all the tricks, but is also very busy at the moment drinking its coffee and doesn't want to be disturbed by anyone."

    memory = SummaryBufferMemory(session=session, buffer_size=5)

    llm = setup_llm(
        model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )

    run_initial_chat_instance(memory=memory, llm=llm, system_message=system_message)


def continue_summary_buffer_chat(session: str, system_message: str) -> None:

    memory = SummaryBufferMemory(session=session, buffer_size=5)

    llm = setup_llm(
        model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )

    run_loop_chat_instance(memory=memory, llm=llm)


def setup_llm(model_path: str, n_ctx: int, chat_format: str, verbose: bool) -> Llama:

    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        chat_format=chat_format,
        verbose=verbose,
    )
    return llm


def run_initial_chat_instance(
    memory: SummaryBufferMemory, llm: Llama, system_message: str
):
    user_message = input("What would you like to tell the chatbot?\n")

    prompt = memory.create_initial_summary_buffer_prompt(
        system_message=system_message, user_message=user_message
    )

    output = llm.create_chat_completion(
        messages=prompt,
        max_tokens=None,
        stop=["<|end_of_turn|>"],
    )

    print(output)

    chatbot_answer = output["choices"][0]["message"]["content"]  # type: ignore

    memory.update_initial_buffer(
        system_message=system_message,
        user_message=user_message,
        chatbot_answer=chatbot_answer,  # type: ignore
    )

    run_loop_chat_instance(memory=memory, llm=llm)


def run_loop_chat_instance(memory: SummaryBufferMemory, llm: Llama) -> None:

    while True:

        user_message = input("What would you like to tell the chatbot?\n")

        prompt = memory.create_summary_buffer_prompt(user_message=user_message)

        output = llm.create_chat_completion(
            messages=prompt,
            max_tokens=None,
            stop=[
                "<|end_of_turn|>"
            ],  # Stop generating just before the model would generate a new question
        )

        print(output)

        chatbot_answer = output["choices"][0]["message"]["content"]  # type: ignore

        memory.update_summary_buffer(
            llm=llm, user_message=user_message, chatbot_answer=chatbot_answer
        )


start_summary_buffer_chat(session="test")
