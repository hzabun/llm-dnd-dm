import json
from typing import Any, Dict, Iterable, List

from llama_cpp import Llama

from src.llm_dnd_dm import memory, prompts


class DungeonMaster:

    def __init__(
        self, session_name: str, system_message: str, is_new_chat: bool
    ) -> None:
        self.system_message = system_message
        self.is_new_chat = is_new_chat
        self.summary_buffer_memory = memory.SummaryBufferMemory(
            buffer_size=5, session_name=session_name
        )
        self.vector_store_memory = memory.VectorStoreMemory(
            num_query_results=2, session=session_name
        )
        self.llm = Llama(
            model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
            n_ctx=2048,
            chat_format="openchat",
            verbose=False,
            n_gpu_layers=-1,
        )

        self.add_session_to_list(session=session_name)
        self.session_list = self.get_session_list()
        self.summary_buffer_memory.initialize_general_session_on_disk()

    def change_session(self, session_name: str) -> None:
        self.summary_buffer_memory.set_session(session=session_name)
        self.vector_store_memory.set_session(session=session_name)

    def get_full_chat_history(self) -> str:
        chat_messages = self.vector_store_memory.collection.get()["documents"]
        chat_history_str = ""
        if chat_messages:
            for line in chat_messages:
                chat_history_str += line.capitalize() + "\n\n"

        return chat_history_str

    def create_dm_answer(self, user_message: str) -> Any:
        if self.is_new_chat:
            initial_prompt = self.assign_multiple_roles_to_messages(
                ["system", "user"], [self.system_message, user_message]
            )
            chatbot_token_generator = self.inference_llm_generator(initial_prompt)

            for chunk in chatbot_token_generator:
                current_token = chunk["choices"][0]["delta"].get("content", "")
                yield current_token

        else:
            chat_prompt = self.create_prompt_for_dm(user_message=user_message)
            chatbot_token_generator = self.inference_llm_generator(prompt=chat_prompt)

            for chunk in chatbot_token_generator:
                current_token = chunk["choices"][0]["delta"].get("content", "")
                yield current_token

    def create_prompt_for_dm(self, user_message: str) -> List[Dict[str, str]]:
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

    def save_answer_on_disk(
        self, user_message: str, dungeon_master_answer: str
    ) -> None:
        if self.is_new_chat:
            initial_prompt = self.assign_multiple_roles_to_messages(
                ["system", "user"], [self.system_message, user_message]
            )
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
    ) -> None:
        chatbot_answer_formatted = self.assign_role_to_message(
            role="assistant", message=chatbot_answer
        )
        new_lines = initial_lines + [chatbot_answer_formatted]

        self.summary_buffer_memory.save_buffer_on_disk(
            new_lines=new_lines, is_new_chat=self.is_new_chat
        )
        self.summary_buffer_memory.update_buffer_counter()
        self.vector_store_memory.save_new_lines_as_vectors(new_lines=new_lines)
        self.is_new_chat = False

    def save_subsequent_chatbot_answer_on_disk(
        self, new_lines: List[Dict[str, str]]
    ) -> None:
        self.vector_store_memory.save_new_lines_as_vectors(new_lines=new_lines)

        if not self.summary_buffer_memory.summary_pending:
            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, is_new_chat=self.is_new_chat
            )
            self.summary_buffer_memory.update_buffer_counter()

        else:
            new_summary = self.generate_new_summary()
            self.summary_buffer_memory.save_summary_on_disk(new_summary=new_summary)
            self.summary_buffer_memory.reset_buffer_on_disk()
            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, is_new_chat=self.is_new_chat
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

    def inference_llm_generator(self, prompt: List[Any]) -> Iterable:
        output = self.llm.create_chat_completion(
            messages=prompt, max_tokens=None, stop=["<|end_of_turn|>"], stream=True
        )
        return output

    def inference_llm(self, prompt: List[Any]) -> Dict[str, Any]:
        output = self.llm.create_chat_completion(
            messages=prompt, max_tokens=None, stop=["<|end_of_turn|>"], stream=False
        )
        return output

    # def inference_llm_generator(self, prompt: List[Any]) -> Iterable:
    #     for i in range(10):
    #         yield {"choices": [{"delta": {"content": f"{i}"}}]}

    # def inference_llm(self, prompt: List[Any]) -> Dict[str, Any]:

    #     return {
    #         "choices": [
    #             {
    #                 "message": {
    #                     "content": "Test string1, test string 2, test string 3, test string 4, test string 5, test string 6"
    #                 }
    #             },
    #             {
    #                 "message": {
    #                     "content": "Test string10, test string 20, test string 30, test string 40, test string 50, test string 60"
    #                 }
    #             },
    #             {
    #                 "message": {
    #                     "content": "Test string100, test string 200, test string 300, test string 400, test string 500, test string 600"
    #                 }
    #             },
    #         ]
    #     }

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:
        return {"role": role, "content": message}

    def assign_multiple_roles_to_messages(
        self, roles: List[str], messages: List[str]
    ) -> List[Dict[str, str]]:
        formatted_messages = [
            {"role": role, "content": message} for role, message in zip(roles, messages)
        ]

        return formatted_messages

    # TODO convert to property decorator
    def get_session_list(self) -> List[str]:
        with open(
            "src/llm_dnd_dm/history_logs/sessions.json",
            "r",
        ) as f:
            sessions = json.load(f)

        return sessions

    def add_session_to_list(self, session: str) -> None:
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

    def setup_new_session(self, session: str) -> None:
        self.is_new_chat = True
        if session in self.get_session_list():
            self.vector_store_memory.reset_collection(session=session)
        else:
            self.add_session_to_list(session=session)
        self.change_session(session_name=session)
