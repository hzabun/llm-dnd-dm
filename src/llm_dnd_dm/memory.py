from prompts import (
    prepare_summarizer_prompt,
    prepare_buffer_summary_chat_prompt,
)
import json
from typing import Any, List, Dict, Union


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

        if new_chat:
            with open(
                "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
                + self.session
                + ".json",
                "w",
            ) as f:
                new_lines_formatted = ["", new_lines]
                json.dump(new_lines_formatted, f, indent=4)

        else:
            with open(
                "src/llm_dnd_dm/history_logs/summary_buffer_lines/"
                + self.session
                + ".json",
                "r+",
            ) as f:

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

    def create_initial_summary_buffer_prompt(
        self, system_message: str, user_message: str
    ) -> List[Any]:

        formatted_messages = self.assign_multiple_roles_to_messages(
            ["system", "user"], [system_message, user_message]
        )

        return formatted_messages

    def update_initial_buffer(
        self, system_message: str, user_message: str, chatbot_answer: str
    ):
        formatted_messages = self.assign_multiple_roles_to_messages(
            ["system", "user", "assistant"],
            [system_message, user_message, chatbot_answer],
        )

        self.save_buffer_on_disk(formatted_messages, new_chat=True)

    def create_summary_buffer_prompt(self, user_message: str) -> List[Any]:

        current_summary = self.load_context_from_disk()
        last_messages = self.load_buffer_from_disk()

        system_summary_prompt = prepare_buffer_summary_chat_prompt(
            current_summary=current_summary, new_messages=last_messages
        )

        formatted_messages = self.assign_multiple_roles_to_messages(
            ["system", "user"], [system_summary_prompt, user_message]
        )

        return formatted_messages

    def update_summary_buffer(self, llm, user_message: str, chatbot_answer: Any):

        formatted_messages = self.assign_multiple_roles_to_messages(
            ["user", "assistant"],
            [user_message, chatbot_answer],
        )

        self.buffer_counter += 2

        if self.buffer_counter < self.buffer_size:

            self.save_buffer_on_disk(
                new_lines=formatted_messages,
                new_chat=False,
            )

        else:

            current_summary = self.load_context_from_disk()
            current_buffer = self.load_buffer_from_disk()
            current_buffer += formatted_messages

            summary_prompt = prepare_summarizer_prompt(
                current_summary=current_summary, new_messages=current_buffer
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

            self.reset_buffer_on_disk()
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
