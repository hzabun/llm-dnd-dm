from typing import List, Optional, Union

import customtkinter

from src.llm_dnd_dm.chatbot import DungeonMaster

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class StartNewSessionWindow(customtkinter.CTkToplevel):
    def __init__(self, sessions: List[str]) -> None:

        super().__init__()

        self._user_input: Union[str, None] = None
        self._running: bool = False
        self._title = "Start a new session"
        self._text = "Choose existing or type a new session"

        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._create_widgets(sessions=sessions)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self, sessions: List[str]) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(
            master=self,
            width=300,
            wraplength=300,
            text=self._text,
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.sessions_combobox = customtkinter.CTkComboBox(master=self, values=sessions)
        self.sessions_combobox.grid(row=1, column=0, padx=(20, 20), pady=(20, 20))

        self.ok_button = customtkinter.CTkButton(
            master=self, width=100, border_width=0, text="Ok", command=self._ok_event
        )
        self.ok_button.grid(
            row=2, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew"
        )

        self.cancel_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Cancel",
            command=self._cancel_event,
        )
        self.cancel_button.grid(
            row=2, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew"
        )

    def _ok_event(self, event=None) -> None:
        self._user_input = self.sessions_combobox.get()
        self.grab_release()
        self.destroy()

    def _on_closing(self) -> None:
        self.grab_release()
        self.destroy()

    def _cancel_event(self) -> None:
        self.grab_release()
        self.destroy()

    def get_input(self) -> Optional[str]:
        self.master.wait_window(self)
        return self._user_input


class ContinueSessionWindow(customtkinter.CTkToplevel):
    def __init__(self, sessions: List[str]) -> None:

        super().__init__()

        self._user_input: Union[str, None] = None
        self._running: bool = False
        self._title = "Continue session"
        self._text = "Choose a session"

        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._create_widgets(sessions=sessions)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self, sessions: List[str]) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(
            master=self,
            width=300,
            wraplength=300,
            text=self._text,
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.sessions_option_menu = customtkinter.CTkOptionMenu(
            master=self, values=sessions
        )
        self.sessions_option_menu.grid(row=1, column=0, padx=(20, 20), pady=(20, 20))

        self.ok_button = customtkinter.CTkButton(
            master=self, width=100, border_width=0, text="Ok", command=self._ok_event
        )
        self.ok_button.grid(
            row=2, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew"
        )

        self.cancel_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Cancel",
            command=self._cancel_event,
        )
        self.cancel_button.grid(
            row=2, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew"
        )

    def _ok_event(self, event=None) -> None:
        self._user_input = self.sessions_option_menu.get()
        self.grab_release()
        self.destroy()

    def _on_closing(self) -> None:
        self.grab_release()
        self.destroy()

    def _cancel_event(self) -> None:
        self.grab_release()
        self.destroy()

    def get_input(self) -> Optional[str]:
        self.master.wait_window(self)
        return self._user_input


class App(customtkinter.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("LLM DnD DM")
        self.geometry(f"{800}x{580}")

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=5)
        self.grid_rowconfigure(3, weight=1)
        self.dungeon_master = DungeonMaster(
            session_name="general",
            system_message=general_system_message,
            is_new_chat=True,
        )

        self.start_new_session_window = None
        self.continue_session_window = None

        self.create_widgets()

    def create_widgets(self) -> None:

        self.chat_history = customtkinter.CTkTextbox(self)
        self.chat_history.configure(state="disabled")
        self.chat_history.grid(
            row=0, rowspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew"
        )

        self.user_input_entry = customtkinter.CTkEntry(
            self, placeholder_text="What do you do?"
        )
        self.user_input_entry.grid(
            row=3, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew"
        )
        self.user_input_entry.bind("<Return>", self.user_input_button_action)

        self.user_input_button = customtkinter.CTkButton(
            self, text="Send", command=self.user_input_button_action
        )
        self.user_input_button.grid(
            row=3, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew"
        )

        self.start_new_session_button = customtkinter.CTkButton(
            self, text="Start new session", command=self.start_new_session
        )
        self.start_new_session_button.grid(row=0, column=1, padx=10, pady=(10, 10))
        self.continue_session_button = customtkinter.CTkButton(
            self, text="Continue session", command=self.continue_specific_session
        )
        self.continue_session_button.grid(row=1, column=1, padx=10, pady=(10, 10))

        self.summarizing_label = customtkinter.CTkLabel(
            self,
            text="LLM is currently summarizing chat history!",
            wraplength=200,
            text_color="red",
        )
        self.summarizing_label.grid(row=2, column=1)
        self.summarizing_label.grid_remove()

    # entry bind sends pressed key event as argument, proper catching of argument necessary in method
    def user_input_button_action(self, event=None) -> None:
        prompt = self.user_input_entry.get()
        self.user_input_entry.delete(0, customtkinter.END)
        self.update()

        dungeon_master_answer = self.add_dm_answer_to_chat_history(prompt=prompt)
        self.update_dm_memory(prompt=prompt, dm_answer=dungeon_master_answer)

    def add_dm_answer_to_chat_history(self, prompt: str) -> str:
        self.chat_history.configure(state="normal")
        self.chat_history.insert(
            customtkinter.END,
            "User: " + prompt + "\n\n" + "Dungeon Master: ",
        )
        dungeon_master_answer = ""

        for token in self.dungeon_master.create_dm_answer(user_message=prompt):
            self.chat_history.insert(customtkinter.END, token)
            self.update()
            dungeon_master_answer += token

        self.chat_history.insert(customtkinter.END, "\n\n")
        self.chat_history.configure(state="disabled")

        return dungeon_master_answer

    def update_dm_memory(self, prompt: str, dm_answer: str) -> None:
        if self.dungeon_master.summary_buffer_memory.summary_pending:
            self.summarizing_label.grid()
            self.update()
            self.dungeon_master.save_answer_on_disk(
                user_message=prompt, dungeon_master_answer=dm_answer
            )
            self.summarizing_label.grid_remove()
            self.update()

        else:
            self.dungeon_master.save_answer_on_disk(
                user_message=prompt, dungeon_master_answer=dm_answer
            )

    def start_new_session(self) -> None:
        available_sessions = self.dungeon_master.get_session_list()
        session_window = StartNewSessionWindow(available_sessions)
        selected_session = session_window.get_input()

        if selected_session:
            self.dungeon_master.setup_new_session(session=selected_session)
            self.chat_history.configure(state="normal")
            self.chat_history.delete("0.0", customtkinter.END)
            self.chat_history.configure(state="disabled")

    def continue_specific_session(self) -> None:
        available_sessions = self.dungeon_master.get_session_list()
        session_window = ContinueSessionWindow(available_sessions)
        selected_session = session_window.get_input()

        if selected_session:
            self.dungeon_master.change_session(session_name=selected_session)
            self.chat_history.configure(state="normal")
            self.chat_history.delete("0.0", customtkinter.END)
            self.chat_history.insert("0.0", self.dungeon_master.get_full_chat_history())
            self.chat_history.configure(state="disabled")


general_system_message = "The AI assistant is a world-renowned dungeon master of the fantasy tabletop role-playing game 'Dungeons & Dragons'. The AI assistant always stays in character as the dungeon master. The AI assistant listens to what actions the user takes and guides the story the game. The AI assistant keeps the answers to a couple of sentences."


if __name__ == "__main__":
    app = App()
    app.mainloop()
