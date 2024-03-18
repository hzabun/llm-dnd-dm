import tkinter
import tkinter.messagebox

import customtkinter as ctk
from chatbot import DungeonMaster

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("LLM DnD DM")
        self.geometry(f"{800}x{580}")

        # configure grid
        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=10)
        self.grid_rowconfigure(1, weight=1)
        self.dungeon_master = DungeonMaster(
            session_name="pizza", system_message=pizza_system_message, new_chat=True
        )

        self.create_widgets()

    def create_widgets(self):

        # chat history
        self.chat_history = ctk.CTkTextbox(self)
        self.chat_history.configure(state="disabled")
        self.chat_history.grid(row=0, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # user input entry
        self.user_input_entry = ctk.CTkEntry(
            self, placeholder_text="Tell the Dungen Master something..."
        )
        self.user_input_entry.grid(
            row=1, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew"
        )

        self.user_input_entry.bind("<Return>", self.user_input_button_action)

        # user input button
        self.user_input_button = ctk.CTkButton(
            self, text="Send", command=self.user_input_button_action
        )
        self.user_input_button.grid(
            row=1, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew"
        )
        self.session_combobox = ctk.CTkComboBox(
            master=self,
            values=self.dungeon_master.get_session_list(),
            command=self.session_combobox_callback,
        )
        self.session_combobox.grid(row=0, column=1, padx=(20, 20), pady=(20, 20))
        self.session_combobox.set(
            self.dungeon_master.session_list[0]
        )  # set initial value

    # FIXME: entry bind sends pressed key as argument, proper catching of argument necessary in method
    def user_input_button_action(self, enterKey=None):
        prompt = self.user_input_entry.get()
        self.user_input_entry.delete(0, ctk.END)
        self.chat_history.configure(state="normal")

        self.chat_history.insert(
            ctk.END,
            "User: " + prompt + "\n" + "Dungeon Master: ",
        )
        for token in self.dungeon_master.create_answer(user_message=prompt):

            self.chat_history.insert(ctk.END, token)
            self.update()

        self.chat_history.insert(ctk.END, "\n\n")
        self.chat_history.configure(state="disabled")

    def session_combobox_callback(self, choice):
        print("Chosen session: ", choice)


# chess_system_message = "The AI assistant is a worldclass chess player knowing all the tricks, but is also very busy at the moment drinking its coffee and doesn't want to be disturbed by anyone."

pizza_system_message = (
    "The AI assistant is an owner of a small italian pizza restaurant."
)


# continue_chat(session="pizza", system_message=pizza_system_message)

if __name__ == "__main__":
    app = App()
    app.mainloop()
