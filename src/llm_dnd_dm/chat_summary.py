from llama_cpp import Llama
from memory import SummaryMemory
from typing import Optional


def setup_llm() -> Llama:

    llm = Llama(
        model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )
    return llm


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

        memory.save_context_on_disk(new_summary=new_summary)

        system_message = None


def start_summary_memory_chat(session: str) -> None:

    memory = SummaryMemory(session=session)

    system_message = "You are a worldclass chess player knowing all the tricks, but you're very busy at the moment drinking your coffee and don't want to be disturbed by anyone."

    llm = setup_llm()

    run_summary_memory_chat_instance(
        memory=memory, llm=llm, system_message=system_message
    )


def continue_summary_memory_chat(session: str) -> None:

    memory = SummaryMemory(session=session)

    llm = setup_llm()

    run_summary_memory_chat_instance(memory=memory, llm=llm, system_message=None)


start_summary_memory_chat(session="test")
