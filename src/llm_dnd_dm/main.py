from llama_cpp import Llama
from memory import MessagesMemory, SummaryMemory
from typing import Any, Optional


def setup_llm(
    model_path: str, n_ctx: int, chat_format: str, verbose: bool = False
) -> Llama:

    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        chat_format=chat_format,
        verbose=verbose,
    )
    return llm


def run_basic_memory_chat_instance(
    memory: MessagesMemory, llm: Llama, session: str
) -> None:

    while True:

        user_message = input("What would you like to tell the chatbot?\n")

        prompt = memory.create_basic_message_prompt(
            user_message=user_message,
            session=session,
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


def start_new_basic_memory_chat() -> None:

    memory = MessagesMemory()

    llm = setup_llm(
        "src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )

    system_message = "You are a worldclass chess player knowing all the tricks, but you're very busy at the moment drinking your coffee and don't want to be disturbed by anyone."
    memory.create_system_prompt(system_message=system_message, session="test")

    run_basic_memory_chat_instance(memory=memory, llm=llm, session="test")


def continue_basic_memory_chat() -> None:

    memory = MessagesMemory()

    llm = setup_llm(
        "src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )

    run_basic_memory_chat_instance(memory=memory, llm=llm, session="test")


def run_summary_memory_chat_instance(
    memory: SummaryMemory, llm: Llama, system_message: Optional[str]
) -> None:

    while True:

        user_message = input("What would you like to tell the chatbot?\n")

        prompt = memory.create_summary_prompt(
            user_message=user_message, system_message=system_message
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

        chatbot_answer = output["choices"][0]["message"]  # type: ignore

        new_summary = memory.summarize_new_context(
            llm=llm, user_message=user_message, chatbot_answer=chatbot_answer
        )

        memory.save_context(new_summary=new_summary)

        system_message = None


def start_summary_memory_chat() -> None:

    memory = SummaryMemory("test")

    system_message = "You are a worldclass chess player knowing all the tricks, but you're very busy at the moment drinking your coffee and don't want to be disturbed by anyone."

    llm = setup_llm(
        "src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )

    run_summary_memory_chat_instance(
        memory=memory, llm=llm, system_message=system_message
    )


def continue_summary_memory_chat() -> None:

    memory = SummaryMemory(session="test")

    llm = setup_llm(
        "src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )

    run_summary_memory_chat_instance(memory=memory, llm=llm, system_message=None)


start_summary_memory_chat()
