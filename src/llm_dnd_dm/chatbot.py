from llama_cpp import Llama
import memory
from typing import List, Dict
from prompts import prepare_system_chat_prompt, prepare_summarizer_prompt


class DungeonMaster:

    def __init__(self, session: str, system_message: str, new_chat: bool) -> None:
        self.system_message = system_message
        self.new_chat = new_chat
        self.session = session
        self.summary_buffer_memory = memory.SummaryBufferMemory(buffer_size=5)
        self.vector_store_memory = memory.VectorStoreMemory()
        self.llm = Llama(
            model_path="src/llm_dnd_dm/llm_weights/openchat_3.5.Q4_K_M.gguf",
            n_ctx=2048,
            chat_format="openchat",
            verbose=False,
        )

    def respond_to_user(self, user_message: str) -> str:
        if self.new_chat:

            roles = ["system", "user"]
            messages = [self.system_message, user_message]

            initial_prompt = self.assign_multiple_roles_to_messages(
                roles=roles, messages=messages
            )

            chatbot_answer = str(self.inference_llm(initial_prompt))

            self.save_initial_chatbot_answer_on_disk(
                initial_lines=initial_prompt, chatbot_answer=chatbot_answer
            )

            self.new_chat = False

            return chatbot_answer
        else:

            current_summary = self.summary_buffer_memory.load_summary_from_disk(
                session=self.session
            )

            last_messages = self.summary_buffer_memory.load_buffer_from_disk(
                session=self.session
            )

            user_message_formatted = self.assign_role_to_message("user", user_message)

            if not current_summary:

                chat_prompt = last_messages + [user_message_formatted]

            else:
                system_prompt = prepare_system_chat_prompt(
                    current_summary=current_summary,
                    context_sentence="",
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
            new_lines=new_lines, session=self.session, new_chat=self.new_chat
        )

        self.summary_buffer_memory.buffer_counter += 2

    def save_subsequent_chatbot_answer_on_disk(self, new_lines: List[Dict[str, str]]):

        if (
            self.summary_buffer_memory.buffer_counter
            < self.summary_buffer_memory.buffer_size
        ):

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, session=self.session, new_chat=False
            )

            self.summary_buffer_memory.buffer_counter += 2

        else:

            current_summary = self.summary_buffer_memory.load_summary_from_disk(
                self.session
            )

            summarizer_prompt = prepare_summarizer_prompt(
                current_summary=current_summary, new_lines=new_lines
            )

            new_summary = self.inference_llm(summarizer_prompt)

            self.summary_buffer_memory.save_summary_on_disk(
                new_summary=new_summary, session=self.session
            )

            self.summary_buffer_memory.reset_buffer_on_disk(self.session)

            self.summary_buffer_memory.save_buffer_on_disk(
                new_lines=new_lines, session=self.session, new_chat=self.new_chat
            )

            self.summary_buffer_memory.buffer_counter = 2

    def update_summary_buffer(self):
        pass

    def inference_llm(self, prompt):
        output = self.llm.create_chat_completion(
            messages=prompt,
            max_tokens=None,
            stop=["<|end_of_turn|>"],
        )

        return output["choices"][0]["message"]["content"]  # type: ignore

    def assign_multiple_roles_to_messages(
        self, roles: List[str], messages: List[str]
    ) -> List[Dict[str, str]]:

        formatted_messages = []

        for role, message in zip(roles, messages):
            formatted_messages.append({"role": role, "content": message})

        return formatted_messages

    def assign_role_to_message(self, role: str, message: str) -> Dict[str, str]:

        return {"role": role, "content": message}
