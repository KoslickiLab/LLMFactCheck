import csv
import os
from typing import Any, List, Tuple, Union
from src.progress_path import PROGRESS_FILES


def read_progress(model_name: str) -> Union[List[Tuple[int, ...]], List[Any]]:
    """
    Read the progress of a specified model from its corresponding CSV file.

    Parameters:
    model_name (str): The name of the model for which progress needs to be read.
                      Valid values are keys of the PROGRESS_FILES dictionary.

    Returns:
    Union[List[Tuple[int, ...]], List[Any]]: A list of tuples, where each tuple
                                             represents a row in the CSV file.
                                             Returns an empty list if file is not found.

    Raises:
    ValueError: If the model_name is not a valid key in PROGRESS_FILES.
    """
    progress_file = PROGRESS_FILES.get(model_name)
    if not progress_file:
        raise ValueError("Invalid model name")

    try:
        with open(progress_file, "r") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            return [tuple(map(int, row)) for row in reader]
    except FileNotFoundError:
        return []


def write_progress(model_key, sentence_id, predicate_id):

    """
    Write a progress record to the CSV file of a specified model.

    Parameters:
    model_name (str): The name of the model for which progress needs to be written.
                      Valid values are keys of the PROGRESS_FILES dictionary.
    sentence_id (int): The ID of the sentence for which progress is being tracked.
    predicate_id (int): The ID of the predicate for which progress is being tracked.

    Raises:
    ValueError: If the model_name is not a valid key in PROGRESS_FILES.
    """
    progress_file = PROGRESS_FILES.get(model_key)
    if not progress_file:
        raise ValueError(f"Invalid model name: {model_key}")

    file_exists = os.path.isfile(progress_file)
    is_empty = os.stat(progress_file).st_size == 0 if file_exists else False
    with open(progress_file, "a", newline="") as file:
        writer = csv.writer(file)
        if is_empty or not file_exists:
            writer.writerow(["Sentence ID", "Predicate ID"])
        writer.writerow([sentence_id, predicate_id])
