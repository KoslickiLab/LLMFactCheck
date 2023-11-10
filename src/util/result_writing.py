def write_result_to_csv(writer, predicate_id, predicate_text, sentence_id, sentence, is_correct, result):
    writer.writerow([predicate_id, predicate_text, sentence_id, sentence, is_correct, result])
