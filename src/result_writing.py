import csv


def write_result_to_csv(console_results_writer, predicate_id, triple_text,
                        sentence_id, sentence, is_correct, question, answer):
    """
    Write the results of processing to a CSV file using a CSV writer.

    This function takes various pieces of information related to the processing
    of semantic triples, and writes them to a CSV file. It includes details
    such as predicate ID, the text of the triple, sentence ID, the original
    sentence, correctness of the triple, and any associated question and answer.

    Parameters:
    console_results_writer (csv.writer): A CSV writer object used for writing to a file.
    predicate_id (int): The ID of the predicate.
    triple_text (str): The text of the semantic triple.
    sentence_id (int): The ID of the sentence from which the triple is derived.
    sentence (str): The original sentence.
    is_correct (bool): Flag indicating whether the triple is correct.
    question (str, optional): A related question, if any.
    answer (str, optional): The answer to the related question, if any.

    Returns:
    None
    """
    console_results_writer.writerow([
        predicate_id, triple_text, sentence_id, sentence, is_correct,
        question if question else '',
        answer.strip() if answer else ''
    ])


def write_progress(writer: csv.writer, sentence_id: int, predicate_id: int) -> None:
    """
    Write the progress of processing to a CSV file.

    This function records the current progress of processing by logging the
    sentence ID and predicate ID to a CSV file. It's useful for tracking
    which sentences and predicates have been processed.

    Parameters:
    writer (csv.writer): A CSV writer object used for writing to a file.
    sentence_id (int): The ID of the sentence being processed.
    predicate_id (int): The ID of the predicate being processed.

    Returns:
    None
    """
    writer.writerow([sentence_id, predicate_id])
