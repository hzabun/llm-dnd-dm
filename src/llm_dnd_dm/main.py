from chatbot import DungeonMaster


def start_chat(session: str, system_message: str) -> None:

    dungeon_master = DungeonMaster(
        session=session, system_message=system_message, new_chat=True
    )

    while True:

        user_message = input("What would you like to tell the dungeon master?\n")
        print("-" * 200)

        chatbot_answer = dungeon_master.respond_to_user(user_message=user_message)

        print(chatbot_answer)

        # chatbot_answer = output["choices"][0]["message"]["content"]  # type: ignore


# def continue_chat(session: str, system_message: str) -> None:

#     memory = SummaryBufferMemory(session=session, buffer_size=5)

#     run_loop_chat_instance(memory=memory, llm=llm)


system_message = "The AI assistant is a worldclass chess player knowing all the tricks, but is also very busy at the moment drinking its coffee and doesn't want to be disturbed by anyone."

start_chat(session="test", system_message=system_message)
