from llama_cpp import Llama
import memory

from typing import List, Dict, Optional, Any, Iterable
from prompts import prepare_system_chat_prompt, prepare_summarizer_prompt


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
        self.llm = Llama(
            model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
            n_ctx=2048,
            chat_format="openchat",
            verbose=False,
            n_gpu_layers=-1,
        )

    def create_answer(self, user_message: str):

        if self.new_chat:
            initial_prompt = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message},
            ]

            chatbot_token_generator = self.inference_llm(initial_prompt, stream=True)
            # chatbot_token_generator = self.dummy_generator()
            full_chatbot_answer = ""

            for chunk in chatbot_token_generator:

                current_token = chunk["choices"][0]["delta"].get("content", "")
                full_chatbot_answer += current_token
                yield current_token

            self.save_initial_chatbot_answer_on_disk(
                initial_lines=initial_prompt, chatbot_answer=full_chatbot_answer
            )

            self.new_chat = False

        else:

            chat_prompt = self.create_prompt(user_message=user_message)

            chatbot_token_generator = self.inference_llm(
                prompt=chat_prompt, stream=True
            )
            # chatbot_token_generator = self.dummy_generator()

            full_chatbot_answer = ""

            for chunk in chatbot_token_generator:

                current_token = chunk["choices"][0]["delta"].get("content", "")
                full_chatbot_answer += current_token
                yield current_token

            new_lines_to_save = self.assign_multiple_roles_to_messages(
                ["user", "assistant"], [user_message, full_chatbot_answer]
            )

            self.save_subsequent_chatbot_answer_on_disk(new_lines=new_lines_to_save)

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

            system_prompt = prepare_system_chat_prompt(
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

    def save_subsequent_chatbot_answer_on_disk(self, new_lines: List[Dict[str, str]]):

        self.vector_store_memory.save_new_lines_as_vectors(new_lines=new_lines)

        current_buffer = self.summary_buffer_memory.buffer_counter

        if current_buffer < self.summary_buffer_memory.buffer_size:

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, new_chat=self.new_chat
            )

            self.summary_buffer_memory.update_buffer_counter()

        else:

            current_summary = self.summary_buffer_memory.load_summary_from_disk()

            last_messages = self.summary_buffer_memory.load_buffer_from_disk()

            summarizer_prompt = prepare_summarizer_prompt(
                current_summary=current_summary, new_lines=last_messages
            )

            # new_summary = self.inference_llm(prompt=summarizer_prompt, stream=False)

            new_summary_content = new_summary["choices"][0]["message"]["content"]  # type: ignore

            self.summary_buffer_memory.save_summary_on_disk(
                new_summary=new_summary_content
            )

            self.summary_buffer_memory.reset_buffer_on_disk()

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, new_chat=self.new_chat
            )

            self.summary_buffer_memory.update_buffer_counter()

    def inference_llm(self, prompt: List[Any], stream: bool) -> Iterable:
        output = self.llm.create_chat_completion(
            messages=prompt, max_tokens=None, stop=["<|end_of_turn|>"], stream=stream
        )

        return output

    # def dummy_generator(self):

    #     for i in range(10):
    #         yield {"choices": [{"delta": {"content": "Token number {}".format(i)}}]}

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:

        return {"role": role, "content": message}

    def assign_multiple_roles_to_messages(
        self, roles: List[str], messages: List[str]
    ) -> List[Dict[str, str]]:

        formatted_messages = []

        for role, message in zip(roles, messages):
            formatted_messages.append({"role": role, "content": message})

        return formatted_messages
