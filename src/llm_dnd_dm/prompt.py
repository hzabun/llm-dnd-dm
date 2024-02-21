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


def create_GPT4_correct_prompt(system_prompt: str, messages: list) -> str:

    separator = "<|end_of_turn|>"
    result_prompt = ""
    for message in messages:
        result_prompt += message + separator

    result_prompt = system_prompt + result_prompt + "GPT4 Correct Assistant:"
    # tokens = tokenizer("GPT4 Correct User: Hello<|end_of_turn|>GPT4 Correct Assistant: Hi<|end_of_turn|>GPT4 Correct User: How are you today?<|end_of_turn|>GPT4 Correct Assistant:").input_ids

    return ""
