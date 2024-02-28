import os
import csv
from typing import Tuple, TextIO
import pandas as pd


def read_data_from_files(triple_file: str, sentence_file: str, labeled_dataset_file: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Read data from specified triple and sentence files into pandas DataFrames.

    This function reads two CSV files: one containing triples data and the other containing sentences.
    It sets custom column names for the dataframes and performs basic preprocessing like stripping
    quotes from the sentence strings.

    Parameters:
    triple_file (str): File name of the triples CSV file located in the 'data' directory.
    sentence_file (str): File name of the sentences CSV file located in the 'data' directory.

    Returns:
    Tuple[pd.DataFrame, pd.DataFrame]: A tuple of two pandas DataFrames, one for triples and the other for sentences.
    """
    triple_data = pd.read_csv(os.path.join('data', triple_file), delimiter=',', header=None, engine='python')
    triple_data.columns = [
        "PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE", "SUBJECT_CUI", "SUBJECT_NAME",
        "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY", "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE",
        "OBJECT_NOVELTY", "Column", "Column", "Column"
    ]

    sentence_data = pd.read_csv(os.path.join('data', sentence_file), delimiter=',', header=None, engine='python')
    sentence_data.columns = [
        "SENTENCE_ID", "PMID", "TYPE", "NUMBER", "SENT_START_INDEX", "SENTENCE",
        "SECTION_HEADER", "NORMALIZED_SECTION_HEADER", "Column", "Column"
    ]
    sentence_data["SENTENCE"] = sentence_data["SENTENCE"].str.strip('""')
    labeled_dataset= pd.read_csv(os.path.join('data', labeled_dataset_file), delimiter=',', header=None, engine='python')
    labeled_dataset.columns = [
        "ID" ,"Fact", "Source", "Template", "Reference", "Name"
    ]
    return triple_data, sentence_data, labeled_dataset


def initialize_writers(result_file: str, progress_file_path: str) -> Tuple[csv.writer, csv.writer, TextIO, TextIO]:
    """
    Initialize CSV writers for writing results and progress to files.

    This function opens the specified result and progress files in append mode and
    initializes csv.writer objects for them. It handles exceptions during file opening
    and raises them after logging.

    Parameters:
    result_file (str): The file path for writing result data.
    progress_file_path (str): The file path for writing progress data.

    Returns:
    Tuple[csv.writer, csv.writer, TextIO, TextIO]: A tuple containing two csv.writer objects
                                                    and two file objects for results and progress.
    """
    try:
        console_results_file = open(result_file, mode="a", newline="")
        progress_file = open(progress_file_path, mode="a", newline="")
        console_results_writer = csv.writer(console_results_file)
        progress_writer = csv.writer(progress_file)
        return console_results_writer, progress_writer, console_results_file, progress_file
    except Exception as e:
        print(f"Error initializing writers: {e}")
        raise


def save_state(progress_file_path: str, last_processed: dict) -> None:
    """
    Save the last processed state to a progress file.

    This function writes the last processed sentence ID and predicate ID to the progress file.
    It's used to keep track of progress in case of interruptions during processing.

    Parameters:
    progress_file_path (str): The file path for the progress file.
    last_processed (dict): A dictionary containing the 'sentence_id' and 'predicate_id' of the last processed item.

    Returns:
    None
    """
    with open(progress_file_path, 'a+', newline='') as progress_file:
        csv_writer = csv.writer(progress_file)
        csv_writer.writerow([last_processed['sentence_id'], last_processed['predicate_id']])


def load_state(progress_file_path: str):
    """
    Load the last processed state from a progress file.

    This function reads the progress file to find the last processed sentence ID and predicate ID.
    It's used to resume processing from where it was last stopped.

    Parameters:
    progress_file_path (str): The file path for the progress file.

    Returns:
    dict or None: A dictionary containing the 'sentence_id' and 'predicate_id' of the last processed item,
                  or None if the file does not exist or is empty.
    """
    try:
        with open(progress_file_path, 'r') as progress_file:
            reader = csv.reader(progress_file)
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                return {'sentence_id': int(last_row[0]), 'predicate_id': int(last_row[1])}
            else:
                return None
    except FileNotFoundError:
        return None
