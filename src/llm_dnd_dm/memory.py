from prompt import prepare_summary_prompt
import json
from typing import Any, List, Dict, Union, Optional


class MessagesMemory:

    # chat_sessions: List[str] = []

    def save_messages_on_disk(
        self,
        messages: Union[List[Dict[str, str]], Dict[str, str], Any],
        session: str,
        new_chat: bool,
    ) -> None:

        if new_chat:
            with open(
                "src/llm_dnd_dm/history_logs/basic_message_lines/" + session + ".json",
                "w",
            ) as f:
                data = messages
                json.dump(data, f, indent=4)

        else:
            with open(
                "src/llm_dnd_dm/history_logs/basic_message_lines/" + session + ".json",
                "r+",
            ) as f:
                data = json.load(f)
                data.append(messages)
                f.seek(0)
                json.dump(data, f, indent=4)

    def load_messages_from_disk(self, session: str) -> List[Any]:

        with open(
            "src/llm_dnd_dm/history_logs/basic_message_lines/" + session + ".json", "r"
        ) as f:
            data = json.load(f)

        return data

    def create_basic_message_prompt(self, user_message: str, session: str) -> List[Any]:

        formatted_message = self.assign_role_to_message("user", user_message)
        self.save_messages_on_disk(formatted_message, session, new_chat=False)
        user_prompt = self.load_messages_from_disk(session)

        return user_prompt

    def create_system_prompt(self, system_message: str, session: str) -> None:

        formatted_message = self.assign_role_to_message("system", system_message)
        self.save_messages_on_disk([formatted_message], session, new_chat=True)

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:

        return {"role": role, "content": message}


class SummaryMemory:

    session: str

    def __init__(self, session: str) -> None:
        self.session = session

    def save_context(self, new_summary: Union[str, Any]) -> None:

        with open(
            "src/llm_dnd_dm/history_logs/chat_summaries/" + self.session + ".txt", "w"
        ) as f:

            if new_summary is not None:
                f.write(new_summary)
            else:
                print("new summary is of type 'None'")

    def load_context(self) -> str:

        with open(
            "src/llm_dnd_dm/history_logs/chat_summaries/" + self.session + ".txt", "r"
        ) as f:
            context = f.read()

        return context

    def create_summary_prompt(
        self, user_message: str, system_message: Optional[str]
    ) -> List[Any]:

        if system_message:

            system_summary_message = system_message

        else:

            system_summary_message = (
                "Use the following conversation summary between the user and the assistant as context to hold a conversation: "
                + self.load_context()
            )

        formatted_messages = self.assign_multiple_roles_to_messages(
            ["system", "user"], [system_summary_message, user_message]
        )

        return formatted_messages

    def summarize_new_context(self, llm, user_message: str, chatbot_answer: Any) -> str:

        current_summary = self.load_context()

        new_lines = [{"role": "user", "content": user_message}] + [chatbot_answer]

        summary_prompt = prepare_summary_prompt(current_summary, new_lines)

        new_summary = llm.create_chat_completion(
            messages=summary_prompt,
            max_tokens=None,
            stop=[
                "<|end_of_turn|>"
            ],  # Stop generating just before the model would generate a new question
        )

        new_summary_text = new_summary["choices"][0]["message"]["content"]

        return new_summary_text

    def assign_multiple_roles_to_messages(
        self, roles: List[str], messages: List[str]
    ) -> List[Dict[str, str]]:

        formatted_messages = []

        for role, message in zip(roles, messages):
            formatted_messages.append({"role": role, "content": message})

        return formatted_messages
