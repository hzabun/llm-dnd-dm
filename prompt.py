_SUMMARIZER_TEMPLATE = """Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.

EXAMPLE
Current summary:
The user asks how to improve their productivity at work. The AI suggests implementing time management techniques.

New lines of conversation:
User: Can you give examples of time management techniques?
AI: Sure, techniques include the Pomodoro Technique, setting clear goals, prioritizing tasks, and eliminating distractions.

New summary:
The user asks how to improve their productivity at work. The AI suggests implementing time management techniques such as the Pomodoro Technique, setting clear goals, prioritizing tasks, and eliminating distractions.
END OF EXAMPLE

Current summary:
{current_summary}

New lines of conversation:
{new_lines}

Updated summary:"""

def create_summary_prompt(summary: str, new_lines: str) -> str:
    
    return _SUMMARIZER_TEMPLATE.format(summary, new_lines)

