from prompt import create_summary_prompt
import json
from typing import Any


class MessagesMemory:

    def save_messages(self, messages: list[Any]) -> None:
        pass

    def load_messages(self) -> list[Any]:
        with open("history_logs/chess_message_lines.json") as f:
            data = json.load(f)
        return data


class SummaryMemory:

    def save_context(self, new_summary: str) -> None:
        pass

    def load_context(self) -> str:
        return ""

    def summarize_context(self, current_summary: str, new_lines: str, llm) -> None:
        summary_prompt = create_summary_prompt(current_summary, new_lines)

        # new_summary = llm.predict(summary_prompt)

        # self.save_context(new_summary)
