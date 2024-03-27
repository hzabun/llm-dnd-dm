from typing import Any, Dict, List, Union

_SUMMARIZER_SYSTEM_TEMPLATE = "Progressively summarize the new lines of conversation. Use the provided current summary and the new lines of conversation to create an updated summary.\n"

_SUMMARIZER_USER_TEMPLATE = """Current summary:
{current_summary}

New lines of conversation:
{new_lines}

Updated summary:"""


_CHAT_TEMPLATE = """Continue the conversation between you and the user by using the following AI assistant role description, the provided summary of the conversation so far and the supplemental related sentences as context:

AI assistant role description:
{system_message}


Conversation summary:
{current_summary}

Context sentence:
{related_information}
"""


def prepare_summarizer_prompt(
    current_summary: str, new_lines: List[Dict[str, str]]
) -> List[Dict[str, str]]:

    new_lines_formatted = ""

    for line in new_lines:

        new_lines_formatted += line["role"] + ": " + line["content"] + "\n"

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


def prepare_system_chat_prompt(
    system_message: str,
    current_summary: str,
    context_sentences: Union[str, List[Any]],
) -> str:

    context_sentences_formatted = ""

    for sentence in context_sentences:
        context_sentences_formatted += sentence + "\n"

    return _CHAT_TEMPLATE.format(
        system_message=system_message,
        current_summary=current_summary,
        related_information=context_sentences_formatted,
    )


# def create_GPT4_correct_prompt(system_prompt: str, messages: list) -> str:

#     separator = "<|end_of_turn|>"
#     result_prompt = ""
#     for message in messages:
#         result_prompt += message + separator

#     result_prompt = system_prompt + result_prompt + "GPT4 Correct Assistant:"
#     # tokens = tokenizer("GPT4 Correct User: Hello<|end_of_turn|>GPT4 Correct Assistant: Hi<|end_of_turn|>GPT4 Correct User: How are you today?<|end_of_turn|>GPT4 Correct Assistant:").input_ids

#     return ""
