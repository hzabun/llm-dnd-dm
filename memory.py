from prompt import create_summary_prompt


class SummaryMemory:

    def save_context(self, new_summary: str):
        pass

    def load_context(self):
        pass

    def summarize_context(self, current_summary: str, new_lines: str, llm):
        summary_prompt = create_summary_prompt(current_summary, new_lines)

        # new_summary = llm.predict(summary_prompt)

        # self.save_context(new_summary)
