import csv

import pandas as pd

from src.util.llama_interaction import get_llama_result
from src.util.result_writing import write_result_to_csv


def read_data_from_files(predication_file, sentence_file):
    predication_data = pd.read_csv(predication_file, delimiter='","', quotechar='"', header=None, engine='python')
    predication_data.columns = [
        "PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE", "SUBJECT_CUI", "SUBJECT_NAME",
        "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY", "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE", "OBJECT_NOVELTY"
    ]
    predication_data["PREDICATION_ID"] = predication_data["PREDICATION_ID"].str.strip('""')
    predication_data["SENTENCE_ID"] = predication_data["SENTENCE_ID"].str.strip('""')

    sentence_data = pd.read_csv(sentence_file, delimiter='\t', header=None, engine='python')
    sentence_data = sentence_data[0].str.split('","', expand=True)
    sentence_data = sentence_data.apply(lambda x: x.str.strip('"'))
    sentence_data.columns = [
        "SENTENCE_ID", "PMID", "TYPE", "NUMBER", "SENT_START_INDEX", "SENTENCE",
        "SECTION_HEADER", "NORMALIZED_SECTION_HEADER", "Column"
    ]
    sentence_data["SENTENCE_ID"] = sentence_data["SENTENCE_ID"].str.strip('""')

    return predication_data, sentence_data


def process_predicate_row(row):
    sentence_id = row["SENTENCE_ID"]
    predicate_raw = row["PREDICATE"].strip('""_').replace('_', ' ').lower()
    predicate = "is a" if predicate_raw == "isa" else predicate_raw
    subject_name = row["SUBJECT_NAME"].strip('""_')
    object_name = row["OBJECT_NAME"].strip('""_')
    full_predicate = f"{subject_name} {predicate} {object_name}"
    return sentence_id, full_predicate


def process_data_and_fact_check(lcpp_llm, predication_data, sentence_data, result_file):
    sentence_dict = {}
    for index, row in predication_data.iterrows():
        sentence_id, full_predicate = process_predicate_row(row)
        if sentence_id not in sentence_dict:
            sentence_dict[sentence_id] = []
        sentence_dict[sentence_id].append((row["PREDICATION_ID"], full_predicate))

    with open(result_file, mode="w", newline="") as console_results_file:
        console_results_writer = csv.writer(console_results_file)
        console_results_writer.writerow(
            ["Predicate ID", "Predicate", "Sentence ID", "Sentence", "Is Correct", "Result"]
        )

        for sentence_id, predicates_for_sentence in sentence_dict.items():
            if sentence_id in sentence_data['SENTENCE_ID'].values:
                sentence = sentence_data[sentence_data['SENTENCE_ID'] == sentence_id]['SENTENCE'].values[0]

                for predicate_id, predicate_text in predicates_for_sentence:
                    prompt = f"Is the triple '{predicate_text}' supported by the sentence: '{sentence}'"
                    result = get_llama_result(lcpp_llm, prompt)
                    is_correct = "True" if "Yes" in result else "False"

                    write_result_to_csv(console_results_writer, predicate_id, predicate_text, sentence_id, sentence,
                                        is_correct, result)
            else:
                print(f"Sentence ID {sentence_id} not found in sentence_data")
