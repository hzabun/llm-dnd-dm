from llama_cpp import Llama
from memory import MessagesMemory


def setup_llm() -> Llama:

    llm = Llama(
        model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        n_ctx=2048,
        chat_format="openchat",
        verbose=False,
    )
    return llm


def run_basic_memory_chat_instance(memory: MessagesMemory, llm: Llama) -> None:

    while True:

        user_message = input("What would you like to tell the chatbot?\n")

        prompt = memory.create_basic_message_prompt(user_message=user_message)

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

        memory.save_messages_on_disk(chat_answer, new_chat=False)


def start_new_basic_memory_chat(session: str) -> None:

    memory = MessagesMemory(session=session)

    llm = setup_llm()

    system_message = "You are a worldclass chess player knowing all the tricks, but you're very busy at the moment drinking your coffee and don't want to be disturbed by anyone."
    memory.create_system_prompt(system_message=system_message)

    run_basic_memory_chat_instance(memory=memory, llm=llm)


def continue_basic_memory_chat(session: str) -> None:

    memory = MessagesMemory(session=session)

    llm = setup_llm()

    run_basic_memory_chat_instance(memory=memory, llm=llm)


start_new_basic_memory_chat(session="test")
