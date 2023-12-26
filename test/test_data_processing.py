import os
import pandas as pd
import pytest
from src import data_processing

os.makedirs(os.path.join('test', 'test_result'), exist_ok=True)

# Define a constant for the progress file name
PROGRESS_FILE = 'llama_progress.csv'


@pytest.fixture
def sample_data():
    return pd.Series({
        "SENTENCE_ID": 1,
        "PREDICATION_ID": 1,
        "PREDICATE": '"isa"',
        "SUBJECT_NAME": '"subject"',
        "OBJECT_NAME": '"object"'
    })


@pytest.mark.parametrize("file1,file2", [
    ("semmed_triple_data.csv", "semmed_sentence_data.csv")
])
def test_read_data_from_files(file1, file2):
    triple_data, sentence_data = data_processing.read_data_from_files(file1, file2)
    assert isinstance(triple_data, pd.DataFrame)
    assert isinstance(sentence_data, pd.DataFrame)


def test_initialize_writers():
    result_file_path = os.path.join('test', 'test_result', 'llama_semmed_result.csv')
    progress_file_path = os.path.join('test', 'test_result', PROGRESS_FILE)

    (console_results_writer, progress_writer, console_results_file,
     progress_file) = data_processing.initialize_writers(result_file_path, progress_file_path)
    assert console_results_writer is not None
    assert progress_writer is not None
    assert console_results_file is not None
    assert progress_file is not None


def test_save_state():
    state = {'sentence_id': 1, 'predicate_id': 1}
    progress_file_path = os.path.join('test', 'test_result', PROGRESS_FILE)
    data_processing.save_state(progress_file_path, state)

    with open(progress_file_path, 'r') as f:
        last_line = f.readlines()[-1]
    assert last_line == '1,1\n'


def test_load_state():
    expected_state = {'sentence_id': 1, 'predicate_id': 1}
    progress_file_path = os.path.join('test', 'test_result', PROGRESS_FILE)
    state = data_processing.load_state(progress_file_path)
    assert state == expected_state
