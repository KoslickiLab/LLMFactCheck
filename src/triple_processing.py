import pandas as pd
from typing import Tuple


def process_triple_row(row: pd.Series) -> Tuple[int, int, str]:
    """
    Process a row of a DataFrame to extract and format a semantic triple.

    This function takes a pandas Series object representing a row of data,
    extracts the relevant information, and formats it into a semantic triple.
    The function handles special cases in the data formatting, such as
    replacing 'isa' with 'is a', removing specific characters, and converting
    text to lowercase.

    Parameters:
    A single row of a DataFrame, expected to contain the columns
    'SENTENCE_ID', 'PREDICATION_ID', 'PREDICATE', 'SUBJECT_NAME',
    and 'OBJECT_NAME'.

    Returns:
    Tuple[int, int, str]: A tuple containing the sentence ID, predicate ID, and
                          the formatted semantic triple as a string.

    Example:
            "SENTENCE_ID": 1,
            "PREDICATION_ID": 101,
            "PREDICATE": '"_isa_"',
            "SUBJECT_NAME": '"_Cat_"',
            "OBJECT_NAME": '"_Animal_"'

    (1, 101, 'Farm animals is an Animals')
    """
    sentence_id = row["SENTENCE_ID"]
    predicate_id = row["PREDICATION_ID"]
    predicate_raw = row["PREDICATE"].strip('""_').replace('_', ' ').lower()
    predicate = "is a" if predicate_raw == "isa" else predicate_raw
    subject_name = row["SUBJECT_NAME"].strip('""_')
    object_name = row["OBJECT_NAME"].strip('""_')

    triple = f"{subject_name} {predicate} {object_name}"
    return sentence_id, predicate_id, triple
