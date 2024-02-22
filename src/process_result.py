import re
from typing import Tuple


def process_result(result: str) -> Tuple[str, str]:
    """
    Process a result string to extract the answer and determine its correctness.

    The function searches for patterns in the result string to classify the answer
    as 'Yes', 'No', or 'Undefined'. If the result contains 'Yes' or 'No', it is
    considered the answer with the corresponding correctness. If it ends with a
    question mark followed by text, the text is extracted as the answer with
    'Undefined' correctness. Otherwise, the entire result is taken as the answer
    with 'Undefined' correctness.

    Parameters:
    result (str): The result string to be processed.

    Returns:
    Tuple[str, str]: A tuple containing the correctness of the answer ('Yes', 'No',
                     or 'Undefined') and the extracted answer.
    """
    match = re.search(r"\b(Yes|No)\b", result)
    if match:
        answer = result[match.start():]
        is_correct = match.group(0) == 'Yes'
    else:
        match = re.search(r"\?([^?]+)$", result)
        if match:
            answer = match.group(1).strip()
        else:
            answer = result.strip()
        is_correct = "Undefined"
    return is_correct, answer
