from typing import List, Dict, Any

_SUMMARIZER_SYSTEM_TEMPLATE = "Progressively summarize the new lines of conversation. Use the provided current summary and the new lines of conversation to create an updated summary."

_SUMMARIZER_USER_TEMPLATE = """Current summary:
{current_summary}

New lines of conversation:
{new_lines}

Updated summary:"""


_BUFFER_SUMMARY_CHAT_TEMPLATE = """Use the following conversation summary and new message lines between the user and the assistant as context to hold a conversation:
Summary: 
{current_summary}

Last message lines:
{last_lines}
"""


def prepare_summarizer_prompt(
    current_summary: str, new_lines: List[Dict[str, str]]
) -> List[Dict[str, str]]:

    new_lines_formatted = ""

    for new_line in new_lines:

        new_lines_formatted += new_line["role"] + ": " + new_line["content"] + "\n"

    summary_prompt = [
        {"role": "system", "content": _SUMMARIZER_SYSTEM_TEMPLATE},
        {
            "role": "user",
            "content": _SUMMARIZER_USER_TEMPLATE.format(
                current_summary=current_summary, new_lines=new_lines_formatted
            ),
        },
    ]

    return summary_prompt


def prepare_buffer_summary_chat_prompt(
    current_summary: str, last_messages: List[Dict[str, str]]
) -> str:
    new_lines_formatted = ""

    for new_line in last_messages:

        new_lines_formatted += new_line["role"] + ": " + new_line["content"] + "\n"

    return _BUFFER_SUMMARY_CHAT_TEMPLATE.format(
        current_summary=current_summary, last_lines=new_lines_formatted
    )


def create_GPT4_correct_prompt(system_prompt: str, messages: list) -> str:

    separator = "<|end_of_turn|>"
    result_prompt = ""
    for message in messages:
        result_prompt += message + separator

    result_prompt = system_prompt + result_prompt + "GPT4 Correct Assistant:"
    # tokens = tokenizer("GPT4 Correct User: Hello<|end_of_turn|>GPT4 Correct Assistant: Hi<|end_of_turn|>GPT4 Correct User: How are you today?<|end_of_turn|>GPT4 Correct Assistant:").input_ids

    return ""
