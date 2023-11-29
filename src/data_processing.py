import os
import re
import csv
from typing import Tuple, TextIO

import pandas as pd
from llama_cpp import Llama
from src.llama_interaction import get_llama_result
from src.result_writing import write_result_to_csv, write_progress

def read_data_from_files(predication_file: str, sentence_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    predication_data = pd.read_csv(os.path.join('data', predication_file), delimiter=',', header=None, engine='python')
    predication_data.columns = [
        "PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE", "SUBJECT_CUI", "SUBJECT_NAME",
        "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY", "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE", "OBJECT_NOVELTY", "Column", "Column", "Column"
    ]

    sentence_data = pd.read_csv(os.path.join('data', sentence_file), delimiter=',', header=None, engine='python')
    sentence_data.columns = [
        "SENTENCE_ID", "PMID", "TYPE", "NUMBER", "SENT_START_INDEX", "SENTENCE",
        "SECTION_HEADER", "NORMALIZED_SECTION_HEADER", "Column", "Column"
    ]
    sentence_data["SENTENCE"] = sentence_data["SENTENCE"].str.strip('""')
    return predication_data, sentence_data


def process_predicate_row(row: pd.Series) -> Tuple[int, int, str]:
    sentence_id = row["SENTENCE_ID"]
    predicate_id = row["PREDICATION_ID"]
    predicate_raw = row["PREDICATE"].strip('""_').replace('_', ' ').lower()
    predicate = "is a" if predicate_raw == "isa" else predicate_raw
    subject_name = row["SUBJECT_NAME"].strip('""_')
    object_name = row["OBJECT_NAME"].strip('""_')
    full_predicate = f"{subject_name} {predicate} {object_name}"
    return sentence_id, predicate_id, full_predicate


def initialize_writers(result_file: str, progress_file_path: str) -> Tuple[csv.writer, csv.writer, TextIO, TextIO]:
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
    with open(progress_file_path, 'a+', newline='') as progress_file:
        csv_writer = csv.writer(progress_file)
        csv_writer.writerow([last_processed['sentence_id'], last_processed['predicate_id']])


def load_state(progress_file_path: str):
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


def process_sentence(lcpp_llm: Llama, sentence_id: int, sentence: str, predicates_for_sentence: list, progress: set,
                     console_results_writer: csv.writer, progress_writer: csv.writer) -> None:
    global is_correct
    for sentence_id, predicate_id, predicate_text in predicates_for_sentence:
        if (sentence_id, predicate_id) not in progress:
            prompt = f"'Is the triple '{predicate_text}' supported by the sentence: '{sentence}'?"

            result = get_llama_result(lcpp_llm, prompt)
            question = f"Is the triple '{predicate_text}' supported by the sentence: '{sentence}'?"

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

            write_result_to_csv(
                console_results_writer, predicate_id, predicate_text, sentence_id, sentence,
                is_correct, question, answer.strip() if answer else None
            )
            write_progress(progress_writer, sentence_id, predicate_id)
        else:
            print(f"Skipping sentence_id: {sentence_id}, predicate_id: {predicate_id}")


def process_data_and_fact_check(lcpp_llm: Llama, predication_data: pd.DataFrame, sentence_data: pd.DataFrame,
                                result_file: str, progress_file_path: str) -> None:
    sentence_dict = {}

    last_processed = load_state(progress_file_path)

    if last_processed:
        # Skip already processed sentences
        predication_data = predication_data[
            predication_data['SENTENCE_ID'].astype(int) > int(last_processed['sentence_id'])]
        print(
            f"Resuming from sentence_id: {last_processed['sentence_id']}, predicate_id: {last_processed['predicate_id']}"
        )

    (console_results_writer, progress_writer,
     console_results_file, progress_file) = initialize_writers(result_file, progress_file_path)

    if not last_processed:
        console_results_writer.writerow(
            ["Predicate ID", "Predicate", "Sentence ID", "Sentence", "Is Correct", "Question", "Answer"])

    for index, row in predication_data.iterrows():
        sentence_id,  predicate_id, full_predicate = process_predicate_row(row)

        if sentence_id not in sentence_dict:
            sentence_dict[sentence_id] = []

        sentence_dict[sentence_id].append((sentence_id, predicate_id, full_predicate))

    for sentence_id, predicates_for_sentence in sentence_dict.items():
        if sentence_id in sentence_data['SENTENCE_ID'].values:
            sentence = sentence_data[sentence_data['SENTENCE_ID'].astype(int) == int(sentence_id)]['SENTENCE'].values[0]
            process_sentence(
                lcpp_llm, int(sentence_id), sentence, predicates_for_sentence,
                set(), console_results_writer, progress_writer)
        else:
            print(f"Sentence ID {sentence_id} not found in sentence_data")

    print("Processing complete.")
