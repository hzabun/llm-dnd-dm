from typing import List, Dict, Any

_SUMMARIZER_SYTEM_TEMPLATE = """Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.

EXAMPLE
Current summary:
The user asks how to improve their productivity at work. The AI suggests implementing time management techniques.

New lines of conversation:
user: Can you give examples of time management techniques?
assistant: Sure, techniques include the Pomodoro Technique, setting clear goals, prioritizing tasks, and eliminating distractions.

New summary:
The user asks how to improve their productivity at work. The AI suggests implementing time management techniques such as the Pomodoro Technique, setting clear goals, prioritizing tasks, and eliminating distractions.
END OF EXAMPLE\n\n"""

_SUMMARIZER_USER_TEMPLATE = """
Current summary:
{current_summary}

New lines of conversation:
{new_lines}

Updated summary:"""


def prepare_summary_prompt(
    current_summary: str, new_lines: List[Dict[str, str]]
) -> List[Dict[str, str]]:

    new_lines_formatted = ""

    new_lines_formatted += new_lines[0]["role"] + ": " + new_lines[0]["content"] + "\n"
    new_lines_formatted += new_lines[1]["role"] + ": " + new_lines[1]["content"]

    summary_prompt = [
        {"role": "system", "content": _SUMMARIZER_SYTEM_TEMPLATE},
        {
            "role": "user",
            "content": _SUMMARIZER_USER_TEMPLATE.format(
                current_summary=current_summary, new_lines=new_lines_formatted
            ),
        },
    ]

    return summary_prompt


def create_GPT4_correct_prompt(system_prompt: str, messages: list) -> str:

    separator = "<|end_of_turn|>"
    result_prompt = ""
    for message in messages:
        result_prompt += message + separator

    result_prompt = system_prompt + result_prompt + "GPT4 Correct Assistant:"
    # tokens = tokenizer("GPT4 Correct User: Hello<|end_of_turn|>GPT4 Correct Assistant: Hi<|end_of_turn|>GPT4 Correct User: How are you today?<|end_of_turn|>GPT4 Correct Assistant:").input_ids

    return ""
