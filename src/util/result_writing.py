import csv

def write_result_to_csv(console_results_writer, predicate_id, predicate_text, sentence_id, sentence, is_correct, question, answer):
    console_results_writer.writerow([
        predicate_id, predicate_text, sentence_id, sentence, is_correct,
        question if question else '',
        answer.strip() if answer else ''
    ])


def write_progress(writer: csv.writer, sentence_id: int, predicate_id: int) -> None:
    writer.writerow([sentence_id, predicate_id])
