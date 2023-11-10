# src/check/check_results.py

# not yet finalized file


import pandas as pd


def read_check_data(check_file):
    return pd.read_csv(check_file, delimiter='","', quotechar='"', header=None, engine='python')


def check_prediction_against_other_datasets(lcpp_llm, sentence, other_data):
    """
    Check if the prediction is correct by comparing it with other datasets.

    :param lcpp_llm: The LLM model. (Not used in this version)
    :param sentence: Sentence corresponding to the prediction.
    :param other_data: Dictionary containing other dataset information.
    :return: True if the prediction is correct, False otherwise.
    """

    correct_predictions = other_data.get("correct_predictions", [])

    # Check if the prediction is in the list of correct predictions
    is_correct = sentence in correct_predictions

    return is_correct


def compare_results(llm_results, lcpp_llm, other_data):
    discrepancies = []
    for index, row in llm_results.iterrows():
        sentence_id = row["Sentence ID"]
        predicate_text = row["Predicate"]
        is_correct_llm = row["Is Correct"]

        # Check against other data
        is_correct_other_data = check_prediction_against_other_datasets(lcpp_llm, predicate_text, other_data)

        if is_correct_llm != is_correct_other_data:
            discrepancies.append((sentence_id, predicate_text, is_correct_llm, is_correct_other_data))

    return discrepancies
