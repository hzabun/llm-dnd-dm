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


def continue_chat(session: str, system_message: str) -> None:

    dungeon_master = DungeonMaster(
        session=session, system_message=system_message, new_chat=False
    )

    while True:

        user_message = input("What would you like to tell the dungeon master?\n")
        print("-" * 200)

        chatbot_answer = dungeon_master.respond_to_user(user_message=user_message)

        print(chatbot_answer)

        # chatbot_answer = output["choices"][0]["message"]["content"]  # type: ignore


chess_system_message = "The AI assistant is a worldclass chess player knowing all the tricks, but is also very busy at the moment drinking its coffee and doesn't want to be disturbed by anyone."

pizza_system_message = (
    "The AI assistant is an owner of a small italian pizza restaurant."
)

# start_chat(session="pizza", system_message=pizza_system_message)

continue_chat(session="pizza", system_message=pizza_system_message)
