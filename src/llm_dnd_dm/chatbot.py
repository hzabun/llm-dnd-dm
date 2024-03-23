import json
import time
from typing import Any, Dict, Iterable, List, Union

from llama_cpp import Llama

from src.llm_dnd_dm import memory, prompts


class DungeonMaster:

    def __init__(self, session_name: str, system_message: str, new_chat: bool) -> None:
        self.system_message = system_message
        self.new_chat = new_chat
        self.summary_buffer_memory = memory.SummaryBufferMemory(
            buffer_size=5, session_name=session_name
        )
        self.vector_store_memory = memory.VectorStoreMemory(
            num_query_results=2, session=session_name
        )
        # self.llm = Llama(
        #     model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
        #     n_ctx=2048,
        #     chat_format="openchat",
        #     verbose=False,
        #     n_gpu_layers=-1,
        # )

        self.add_session_to_list(session=session_name)
        self.session_list = self.get_session_list()
        self.summary_buffer_memory.initialize_general_session_on_disk()

    def change_session(self, session_name: str):
        self.summary_buffer_memory.set_session(session=session_name)
        self.vector_store_memory.set_session(session=session_name)

    def get_full_chat_history(self):
        temp = self.vector_store_memory.collection.get()["documents"]
        if temp:
            chat_history_str = ""
            for line in temp:
                chat_history_str += line.capitalize() + "\n\n"
            return chat_history_str
        return temp

    def create_answer(self, user_message: str):

        if self.new_chat:
            initial_prompt = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message},
            ]

            chatbot_token_generator = self.inference_llm_generator(initial_prompt)
            # full_chatbot_answer = ""

            for chunk in chatbot_token_generator:

                current_token = chunk["choices"][0]["delta"].get("content", "")
                # full_chatbot_answer += current_token
                yield current_token

            # self.save_initial_chatbot_answer_on_disk(
            #     initial_lines=initial_prompt, chatbot_answer=full_chatbot_answer
            # )

        else:

            chat_prompt = self.create_prompt(user_message=user_message)

            chatbot_token_generator = self.inference_llm_generator(prompt=chat_prompt)

            # full_chatbot_answer = ""

            for chunk in chatbot_token_generator:

                current_token = chunk["choices"][0]["delta"].get("content", "")
                # full_chatbot_answer += current_token
                yield current_token

            # new_lines_to_save = self.assign_multiple_roles_to_messages(
            #     ["user", "assistant"], [user_message, full_chatbot_answer]
            # )

            # self.save_subsequent_chatbot_answer_on_disk(new_lines=new_lines_to_save)

    def create_prompt(self, user_message: str) -> List[Dict[str, str]]:

        current_summary = self.summary_buffer_memory.load_summary_from_disk()

        last_messages = self.summary_buffer_memory.load_buffer_from_disk()

        user_message_formatted = self.assign_role_to_message("user", user_message)

        if not current_summary:

            chat_prompt = last_messages + [user_message_formatted]

            return chat_prompt

        else:

            related_information = self.vector_store_memory.retreive_related_information(
                user_message=user_message
            )

            system_prompt = prompts.prepare_system_chat_prompt(
                current_summary=current_summary,
                context_sentences=related_information,
            )

            system_prompt_formatted = self.assign_role_to_message(
                "system", system_prompt
            )

            chat_prompt = (
                [system_prompt_formatted] + last_messages + [user_message_formatted]
            )

            return chat_prompt

    def save_answer_on_disk(self, user_message: str, dungeon_master_answer: str):
        if self.new_chat:
            initial_prompt = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message},
            ]

            self.save_initial_chatbot_answer_on_disk(
                initial_lines=initial_prompt, chatbot_answer=dungeon_master_answer
            )

        else:
            new_lines_to_save = self.assign_multiple_roles_to_messages(
                ["user", "assistant"], [user_message, dungeon_master_answer]
            )

            self.save_subsequent_chatbot_answer_on_disk(new_lines=new_lines_to_save)

    def save_initial_chatbot_answer_on_disk(
        self, initial_lines: List[Dict[str, str]], chatbot_answer: str
    ):
        chatbot_answer_formatted = self.assign_role_to_message(
            role="assistant", message=chatbot_answer
        )

        new_lines = initial_lines + [chatbot_answer_formatted]

        self.summary_buffer_memory.save_buffer_on_disk(
            new_lines=new_lines, new_chat=self.new_chat
        )

        self.summary_buffer_memory.update_buffer_counter()

        self.vector_store_memory.save_new_lines_as_vectors(new_lines=new_lines)

        self.new_chat = False

    def save_subsequent_chatbot_answer_on_disk(self, new_lines: List[Dict[str, str]]):

        self.vector_store_memory.save_new_lines_as_vectors(new_lines=new_lines)

        if not self.summary_buffer_memory.summary_pending:

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, new_chat=self.new_chat
            )

            self.summary_buffer_memory.update_buffer_counter()

        else:

            new_summary = self.generate_new_summary()

            self.summary_buffer_memory.save_summary_on_disk(new_summary=new_summary)

            self.summary_buffer_memory.reset_buffer_on_disk()

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, new_chat=self.new_chat
            )

            self.summary_buffer_memory.update_buffer_counter()

    def generate_new_summary(self) -> str:

        current_summary = self.summary_buffer_memory.load_summary_from_disk()

        last_messages = self.summary_buffer_memory.load_buffer_from_disk()

        summarizer_prompt = prompts.prepare_summarizer_prompt(
            current_summary=current_summary, new_lines=last_messages
        )

        new_summary = self.inference_llm(prompt=summarizer_prompt)

        return new_summary["choices"][0]["message"]["content"]

    # def inference_llm_generator(self, prompt: List[Any]) -> Iterable:
    #     output = self.llm.create_chat_completion(
    #         messages=prompt, max_tokens=None, stop=["<|end_of_turn|>"], stream=True
    #     )

    #     return output

    # def inference_llm(self, prompt: List[Any]) -> Dict[str, Any]:
    #     output = self.llm.create_chat_completion(
    #         messages=prompt, max_tokens=None, stop=["<|end_of_turn|>"], stream=False
    #     )

    #     return output

    def inference_llm_generator(self, prompt: List[Any]) -> Iterable:
        for i in range(10):
            yield {"choices": [{"delta": {"content": f"{i}"}}]}

    def inference_llm(self, prompt: List[Any]) -> Dict[str, Any]:

        return {
            "choices": [
                {
                    "message": {
                        "content": "Test string1, test string 2, test string 3, test string 4, test string 5, test string 6"
                    }
                },
                {
                    "message": {
                        "content": "Test string10, test string 20, test string 30, test string 40, test string 50, test string 60"
                    }
                },
                {
                    "message": {
                        "content": "Test string100, test string 200, test string 300, test string 400, test string 500, test string 600"
                    }
                },
            ]
        }

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:

        return {"role": role, "content": message}

    def assign_multiple_roles_to_messages(
        self, roles: List[str], messages: List[str]
    ) -> List[Dict[str, str]]:

        formatted_messages = []

        for role, message in zip(roles, messages):
            formatted_messages.append({"role": role, "content": message})

        return formatted_messages

    # TODO convert to property decorator
    def get_session_list(self) -> List[str]:
        with open(
            "src/llm_dnd_dm/history_logs/sessions.json",
            "r",
        ) as f:
            sessions = json.load(f)

        return sessions

    def add_session_to_list(self, session: str):

        try:
            f = open(
                "src/llm_dnd_dm/history_logs/sessions.json",
                "r+",
            )
        except FileNotFoundError:
            with open(
                "src/llm_dnd_dm/history_logs/sessions.json",
                "w+",
            ) as f:
                sessions = [session]
                json.dump(sessions, f, indent=4)
        else:
            with f:
                sessions = json.load(f)
                if session in sessions:
                    return
                sessions.append(session)
                f.seek(0)
                json.dump(sessions, f, indent=4)

    def start_new_session(self, session: str):
        self.new_chat = True
        if session in self.get_session_list():
            self.vector_store_memory.reset_collection(session=session)
        else:
            self.add_session_to_list(session=session)
        self.change_session(session_name=session)
