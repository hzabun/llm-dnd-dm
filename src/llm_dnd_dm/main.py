from chatbot import DungeonMaster
import tkinter
import tkinter.messagebox
import customtkinter as ctk

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

        self.create_widgets()

        self.dungeon_master = DungeonMaster(
            session_name="pizza", system_message=pizza_system_message, new_chat=True
        )

    def create_widgets(self):

        # chat history
        self.chat_history = ctk.CTkTextbox(self)
        self.chat_history.configure(state="disabled")
        self.chat_history.grid(
            row=0, columnspan=2, padx=(20, 20), pady=(20, 0), sticky="nsew"
        )

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
        # session_combobox = ctk.CTkComboBox(
        #     master=self,
        #     values=["option 1", "option 2"],
        #     command=self.session_combobox_callback,
        # )
        # session_combobox.pack(padx=20, pady=10)
        # session_combobox.set("option 2")  # set initial value

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

    # def session_combobox_callback(self, choice):
    #     print("combobox dropdown clicked:", choice)


# chess_system_message = "The AI assistant is a worldclass chess player knowing all the tricks, but is also very busy at the moment drinking its coffee and doesn't want to be disturbed by anyone."

pizza_system_message = (
    "The AI assistant is an owner of a small italian pizza restaurant."
)


# continue_chat(session="pizza", system_message=pizza_system_message)

if __name__ == "__main__":
    app = App()
    app.mainloop()
