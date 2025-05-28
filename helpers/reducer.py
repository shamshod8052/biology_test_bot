from typing import Optional


def text_reducer(text: str, new_length: Optional[int] = None) -> str:
    text = '' if text is None else text
    if new_length:
        return text[:new_length] + ('...' if len(text) > new_length else '')
    return text
