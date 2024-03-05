from llama_cpp import Llama
import memory
from typing import List, Dict
from prompts import prepare_system_chat_prompt, prepare_summarizer_prompt


class DungeonMaster:

    def __init__(self, session: str, system_message: str, new_chat: bool) -> None:
        self.system_message = system_message
        self.new_chat = new_chat
        self.summary_buffer_memory = memory.SummaryBufferMemory(
            buffer_size=5, session=session
        )
        self.vector_store_memory = memory.VectorStoreMemory(
            num_query_results=2, session=session
        )
        self.llm = Llama(
            model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
            n_ctx=2048,
            chat_format="openchat",
            verbose=False,
            n_gpu_layers=-1,
        )

    def respond_to_user(self, user_message: str) -> str:
        if self.new_chat:

            initial_prompt = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message},
            ]

            chatbot_answer = str(self.inference_llm(initial_prompt))

            self.save_initial_chatbot_answer_on_disk(
                initial_lines=initial_prompt, chatbot_answer=chatbot_answer
            )

            self.new_chat = False

            return chatbot_answer
        else:

            current_summary = self.summary_buffer_memory.load_summary_from_disk()

            last_messages = self.summary_buffer_memory.load_buffer_from_disk()

            user_message_formatted = self.assign_role_to_message("user", user_message)

            if not current_summary:

                chat_prompt = last_messages + [user_message_formatted]

            else:

                related_information = (
                    self.vector_store_memory.retreive_related_information(
                        user_message=user_message
                    )
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

            chatbot_answer = str(self.inference_llm(chat_prompt))

            chatbot_answer_formatted = self.assign_role_to_message(
                "assistant", chatbot_answer
            )

            self.save_subsequent_chatbot_answer_on_disk(
                new_lines=[user_message_formatted, chatbot_answer_formatted]
            )

            return chatbot_answer

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

        self.summary_buffer_memory.buffer_counter += 2

        self.vector_store_memory.save_new_lines_as_vectors(new_lines=new_lines)

    def save_subsequent_chatbot_answer_on_disk(self, new_lines: List[Dict[str, str]]):

        self.vector_store_memory.save_new_lines_as_vectors(new_lines=new_lines)

        current_buffer = self.summary_buffer_memory.get_current_buffer_count()

        if current_buffer < self.summary_buffer_memory.buffer_size:

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, new_chat=self.new_chat
            )

            self.summary_buffer_memory.buffer_counter += 2

        else:

            current_summary = self.summary_buffer_memory.load_summary_from_disk()

            last_messages = self.summary_buffer_memory.load_buffer_from_disk()

            summarizer_prompt = prepare_summarizer_prompt(
                current_summary=current_summary, new_lines=last_messages
            )

            new_summary = self.inference_llm(summarizer_prompt)

            self.summary_buffer_memory.save_summary_on_disk(new_summary=new_summary)

            self.summary_buffer_memory.reset_buffer_on_disk()

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, new_chat=self.new_chat
            )

            self.summary_buffer_memory.buffer_counter = 2

    def inference_llm(self, prompt):
        output = self.llm.create_chat_completion(
            messages=prompt,
            max_tokens=None,
            stop=["<|end_of_turn|>"],
        )

        return output["choices"][0]["message"]["content"]  # type: ignore

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:

        return {"role": role, "content": message}

    def assign_multiple_roles_to_messages(
        self, roles: List[str], messages: List[str]
    ) -> List[Dict[str, str]]:

        formatted_messages = []

        for role, message in zip(roles, messages):
            formatted_messages.append({"role": role, "content": message})

        return formatted_messages
