import pytest
from unittest.mock import MagicMock
from src.result_writing import write_result_to_csv, write_progress

@pytest.fixture
def mock_writer(mocker):
    return MagicMock()

def test_write_result_to_csv(mock_writer):
    write_result_to_csv(
        mock_writer,
        predicate_id="predicate_id_test",
        predicate_text="predicate_text_test",
        sentence_id="sentence_id_test",
        sentence="sentence_test",
        is_correct="is_correct_test",
        question="question_test",
        answer="answer_test"
    )
    mock_writer.writerow.assert_called_once_with([
        "predicate_id_test",
        "predicate_text_test",
        "sentence_id_test",
        "sentence_test",
        "is_correct_test",
        "question_test",
        "answer_test"
    ])

def test_write_progress(mock_writer):
    write_progress(
        mock_writer,
        sentence_id=1,
        predicate_id=2
    )
    mock_writer.writerow.assert_called_once_with([1, 2])
