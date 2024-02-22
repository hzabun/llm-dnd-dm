from prompt import create_summary_prompt
import json
from typing import Any, List, Dict, Union


class MessagesMemory:

    chat_sessions: List[str] = []

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

    def create_user_prompt(self, user_message: str, session: str) -> List[Any]:

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

    def save_context(self, new_summary: str) -> None:
        pass

    def load_context(self) -> str:

        return ""

    def summarize_context(self, current_summary: str, new_lines: str, llm) -> None:
        summary_prompt = create_summary_prompt(current_summary, new_lines)

        # new_summary = llm.predict(summary_prompt)

        # self.save_context(new_summary)
