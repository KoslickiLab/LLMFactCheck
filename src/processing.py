import pandas as pd

from src.data_processing import initialize_writers
from src.get_result import get_result
from src.process_result import process_result
from src.progress import read_progress, write_progress
from src.result_writing import write_result_to_csv
from src.triple_processing import process_triple_row


def create_prompt(triple_text, sentence, context=""):
    """
        Constructs a prompt for the model to process.

        Args:
            triple_text (str): The triple text.
            sentence (str): The sentence text.
            context (str, optional): Additional context to include in the prompt. Defaults to "".

        Returns:
            str: The constructed prompt.
    """
    return f"'Is the tripple \"{triple_text}\" supported by the sentence: \"{sentence}\"?"


def process_data(model_info, model_type, use_icl, triple_data: pd.DataFrame, sentence_data: pd.DataFrame,
                 result_file: str, progress_file_path: str):
    print("Initializing data processing...")

    sentence_dict = {}
    model_key = model_type + ('_icl' if use_icl else '')
    progress = set(read_progress(model_key))

    last_processed = max(progress, key=lambda x: (x[0], x[1])) if progress else None
    print(f"Last processed: {last_processed}")

    # Check filtering logic
    if last_processed:
        triple_data = triple_data[triple_data['SENTENCE_ID'].astype(int) >= int(last_processed[0])]

    (console_results_writer, progress_writer, console_results_file,
     progress_file) = initialize_writers(result_file, progress_file_path)

    if not last_processed:
        console_results_writer.writerow(
            ["Predicate ID", "Triple", "Sentence ID", "Sentence", "Is Correct", "Question", "Answer"])

    for index, row in triple_data.iterrows():
        sentence_id, predicate_id, triple = process_triple_row(row)
        if sentence_id not in sentence_dict:
            sentence_dict[sentence_id] = []
        sentence_dict[sentence_id].append((sentence_id, predicate_id, triple))

    for sentence_id, triples in sentence_dict.items():
        sentence = sentence_data[sentence_data['SENTENCE_ID'].astype(int) == int(sentence_id)]['SENTENCE'].values[0]
        for triple in triples:
            process_triple(model_info, sentence_id, sentence, triple,
                           progress, console_results_writer, model_key, use_icl, progress_writer)

    console_results_file.close()
    progress_file.close()
    print("Data processing completed.")


def process_triple(model_info, sentence_id, sentence, triple,
                   progress, console_results_writer, model_key, use_icl, _):

    triple_sentence_id, predicate_id, triple_text = triple
    import time
    time.sleep(5) # Sleep for 3 seconds
    if (triple_sentence_id, predicate_id) not in progress:
        prompt = create_prompt(triple_text, sentence, model_info[1] if use_icl else "")
        result = get_result(model_info, prompt, model_key)

        question = f"Is the triple '{triple_text}' supported by the sentence: '{sentence}'?"
        is_correct, answer = process_result(result)
        write_result_to_csv(console_results_writer, predicate_id, triple_text, sentence_id,
                            sentence, is_correct, question, answer.strip() if answer else None)
        write_progress(model_key, sentence_id, predicate_id)
