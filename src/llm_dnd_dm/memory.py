import json
import chromadb
from typing import Any, List, Dict, Union


class SummaryBufferMemory:

    def __init__(self, buffer_size: int, session: str) -> None:
        self.buffer_size = buffer_size
        self.buffer_counter = 0
        self.session = session

    def save_summary_on_disk(self, new_summary: Union[str, Any]) -> None:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer/" + self.session + ".json",
            "r+",
        ) as f:
            summary_buffer_logs = json.load(f)
            summary_buffer_logs[0] = new_summary
            f.seek(0)
            json.dump(summary_buffer_logs, f, indent=4)

    def save_buffer_on_disk(self, new_lines, new_chat: bool) -> None:

        if new_chat:

            with open(
                "src/llm_dnd_dm/history_logs/summary_buffer/" + self.session + ".json",
                "w",
            ) as f:
                new_lines_formatted = ["", new_lines]
                json.dump(new_lines_formatted, f, indent=4)

        else:

            with open(
                "src/llm_dnd_dm/history_logs/summary_buffer/" + self.session + ".json",
                "r+",
            ) as f:

                summary_buffer_logs = json.load(f)
                summary_buffer_logs[1] += new_lines
                f.seek(0)
                json.dump(summary_buffer_logs, f, indent=4)

    def load_summary_from_disk(self) -> str:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer/" + self.session + ".json",
            "r",
        ) as f:
            summary_buffer_logs = json.load(f)
            latest_summary = summary_buffer_logs[0]

        return latest_summary

    def load_buffer_from_disk(self) -> List[Dict[str, str]]:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer/" + self.session + ".json",
            "r",
        ) as f:

            summary_buffer_logs = json.load(f)
            last_messages = summary_buffer_logs[1]

            return last_messages

    def reset_buffer_on_disk(self) -> None:

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer/" + self.session + ".json",
            "r",
        ) as f:

            summary_buffer_logs = json.load(f)

        with open(
            "src/llm_dnd_dm/history_logs/summary_buffer/" + self.session + ".json",
            "w",
        ) as f:

            summary_buffer_logs[1] = []
            f.seek(0)
            json.dump(summary_buffer_logs, f, indent=4)

    def get_current_buffer_count(self):

        buffer = self.load_buffer_from_disk()

        return len(buffer)


class VectorStoreMemory:

    chroma_client = chromadb.PersistentClient(
        path="src/llm_dnd_dm/history_logs/vectore_store"
    )

    def __init__(self, num_query_results: int, session: str):

        self.num_query_results = num_query_results
        self.collection = self.chroma_client.get_or_create_collection(name=session)

    def save_new_lines_as_vectors(self, new_lines: List[Dict[str, str]]):

        roles_and_contents = self.format_messages(message_lines=new_lines)

        str_ids = self.create_string_ids(len(roles_and_contents))

        self.collection.add(documents=roles_and_contents, ids=str_ids)

    def retreive_related_information(self, user_message: str) -> List[str]:

        results = self.collection.query(
            query_texts=user_message,
            n_results=self.num_query_results,
        )

        return results["documents"][0]  # type: ignore

    def format_messages(self, message_lines: List[Dict[str, str]]) -> List[str]:

        roles_and_contents = []
        for message in message_lines:
            roles_and_contents.append(message["role"] + ": " + message["content"])

        return roles_and_contents

    def create_string_ids(self, doc_count: int) -> List[str]:

        current_id_count = self.collection.count()

        int_ids = list(range(current_id_count, current_id_count + doc_count))

        str_ids = list(map(lambda x: "id" + str(x), int_ids))

        return str_ids
