import pytest
from src.process_result import process_result


@pytest.fixture
def result_yes():
    return "Yes, the statement is correct."


@pytest.fixture
def result_no():
    return "No, the statement is incorrect."


@pytest.fixture
def result_question():
    return "Is the statement correct? It is unclear."


@pytest.fixture
def result_ambiguous():
    return "The statement is ambiguous."


def test_process_result_yes(result_yes):
    is_correct, answer = process_result(result_yes)
    assert is_correct is True
    assert answer == 'Yes, the statement is correct.'


def test_process_result_no(result_no):
    is_correct, answer = process_result(result_no)
    assert is_correct is False
    assert answer == 'No, the statement is incorrect.'


def test_process_result_question(result_question):
    is_correct, answer = process_result(result_question)
    assert is_correct == 'Undefined'
    assert answer == 'It is unclear.'


def test_process_result_ambiguous(result_ambiguous):
    is_correct, answer = process_result(result_ambiguous)
    assert is_correct == 'Undefined'
    assert answer == 'The statement is ambiguous.'
