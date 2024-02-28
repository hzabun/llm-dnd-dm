from prompt import prepare_summarizer_prompt, prepare_buffer_summary_chat_prompt
import json
from typing import Any, List, Dict, Union, Optional
from langchain import memory


class MessagesMemory:

    def __init__(self, session: str) -> None:
        self.session = session

    def save_messages_on_disk(
        self,
        messages: Union[List[Dict[str, str]], Dict[str, str], Any],
        new_chat: bool,
    ) -> None:

        if new_chat:
            with open(
                "src/llm_dnd_dm/history_logs/basic_message_lines/"
                + self.session
                + ".json",
                "w",
            ) as f:
                data = messages
                json.dump(data, f, indent=4)

        else:
            with open(
                "src/llm_dnd_dm/history_logs/basic_message_lines/"
                + self.session
                + ".json",
                "r+",
            ) as f:
                data = json.load(f)
                data.append(messages)
                f.seek(0)
                json.dump(data, f, indent=4)

    def load_messages_from_disk(self) -> List[Any]:

        with open(
            "src/llm_dnd_dm/history_logs/basic_message_lines/" + self.session + ".json",
            "r",
        ) as f:
            data = json.load(f)

        return data

    def create_basic_message_prompt(self, user_message: str) -> List[Any]:

        formatted_message = self.assign_role_to_message("user", user_message)
        self.save_messages_on_disk(messages=formatted_message, new_chat=False)
        user_prompt = self.load_messages_from_disk()

        return user_prompt

    def create_system_prompt(self, system_message: str) -> None:

        formatted_message = self.assign_role_to_message("system", system_message)
        self.save_messages_on_disk(messages=[formatted_message], new_chat=True)

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:

        return {"role": role, "content": message}


class SummaryMemory:

    def __init__(self, session: str) -> None:
        self.session = session

    def save_context_on_disk(self, new_summary: Union[str, Any]) -> None:

        with open(
            "src/llm_dnd_dm/history_logs/summary_lines/" + self.session + ".txt", "w"
        ) as f:

            if new_summary is not None:
                f.write(new_summary)
            else:
                print("new summary is of type 'None'")

    def load_context_from_disk(self) -> str:

        with open(
            "src/llm_dnd_dm/history_logs/summary_lines/" + self.session + ".txt", "r"
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
                + self.load_context_from_disk()
            )

        formatted_messages = self.assign_multiple_roles_to_messages(
            ["system", "user"], [system_summary_message, user_message]
        )

        return formatted_messages

    def summarize_new_context(self, llm, user_message: str, chatbot_answer: Any) -> str:

        current_summary = self.load_context_from_disk()

        new_lines = [{"role": "user", "content": user_message}] + [chatbot_answer]

        summary_prompt = prepare_summarizer_prompt(current_summary, new_lines)

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


class SummaryBufferMemory:

    def __init__(self, session: str, buffer_size: int) -> None:
        self.session = session
        self.buffer_size = buffer_size
        self.buffer_counter = 1

    def save_context_on_disk(self, new_summary: Union[str, Any]) -> None:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
            + self.session
            + ".json",
            "r+",
        ) as f:
            summary_buffer_logs = json.load(f)
            summary_buffer_logs[0] = new_summary
            f.seek(0)
            json.dump(summary_buffer_logs, f, indent=4)

    def save_buffer_on_disk(self, new_lines, new_chat: bool) -> None:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
            + self.session
            + ".json",
            "r+",
        ) as f:

            if new_chat:
                new_lines_formatted = ["", new_lines]
                json.dump(new_lines_formatted, f, indent=4)

            else:
                summary_buffer_logs = json.load(f)
                summary_buffer_logs[1] += new_lines
                f.seek(0)
                json.dump(summary_buffer_logs, f, indent=4)

    def load_context_from_disk(self) -> str:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
            + self.session
            + ".json",
            "r",
        ) as f:
            summary_buffer_logs = json.load(f)
            latest_summary = summary_buffer_logs[0]

        return latest_summary

    def load_buffer_from_disk(self) -> List[Dict[str, str]]:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
            + self.session
            + ".json",
            "r",
        ) as f:

            summary_buffer_logs = json.load(f)
            last_messages = summary_buffer_logs[1]

            return last_messages

    def reset_buffer_on_disk(self) -> None:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
            + self.session
            + ".json",
            "r",
        ) as f:

            summary_buffer_logs = json.load(f)

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
            + self.session
            + ".json",
            "w",
        ) as f:

            summary_buffer_logs[1] = []
            f.seek(0)
            json.dump(summary_buffer_logs, f, indent=4)

    def create_summary_prompt(
        self, user_message: str, system_message: Optional[str]
    ) -> List[Any]:

        if system_message:

            system_summary_message = system_message

            formatted_system_message = self.assign_role_to_message(
                "system", system_message
            )
            self.save_buffer_on_disk(
                new_lines=[formatted_system_message], new_chat=True
            )

        else:

            current_summary = self.load_context_from_disk()
            last_messages = self.load_buffer_from_disk()

            system_summary_message = prepare_buffer_summary_chat_prompt(
                current_summary=current_summary, last_messages=last_messages
            )

        formatted_messages = self.assign_multiple_roles_to_messages(
            ["system", "user"], [system_summary_message, user_message]
        )

        return formatted_messages

    def update_summary_buffer(self, llm, user_message: str, chatbot_answer: Any):

        self.save_buffer_on_disk(
            new_lines=[{"role": "user", "content": user_message}, chatbot_answer],
            new_chat=False,
        )

        self.buffer_counter += 2

        if self.buffer_counter >= self.buffer_size:

            current_summary = self.load_context_from_disk()

            current_buffer = self.load_buffer_from_disk()

            self.reset_buffer_on_disk()

            summary_prompt = prepare_summarizer_prompt(
                current_summary=current_summary, new_lines=current_buffer
            )

            new_summary = llm.create_chat_completion(
                messages=summary_prompt,
                max_tokens=None,
                stop=[
                    "<|end_of_turn|>"
                ],  # Stop generating just before the model would generate a new question
            )

            new_summary_text = new_summary["choices"][0]["message"]["content"]

            self.save_context_on_disk(new_summary_text)

            self.buffer_counter = 0

    def assign_multiple_roles_to_messages(
        self, roles: List[str], messages: List[str]
    ) -> List[Dict[str, str]]:

        formatted_messages = []

        for role, message in zip(roles, messages):
            formatted_messages.append({"role": role, "content": message})

        return formatted_messages

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:

        return {"role": role, "content": message}
