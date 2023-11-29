import os
import pandas as pd
import pytest
from src import data_processing

os.makedirs(os.path.join('test', 'test_result'), exist_ok=True)

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
    ("semmed_predication_data.csv", "semmed_sentence_data.csv")
])
def test_read_data_from_files(file1, file2):
    predication_data, sentence_data = data_processing.read_data_from_files(file1, file2)
    assert isinstance(predication_data, pd.DataFrame)
    assert isinstance(sentence_data, pd.DataFrame)


def test_process_predicate_row(sample_data):
    sentence_id, predicate_id, full_predicate = data_processing.process_predicate_row(sample_data)
    assert sentence_id == 1
    assert predicate_id == 1
    assert full_predicate == "subject is a object"

def test_initialize_writers():
    console_results_writer, progress_writer, console_results_file, progress_file = data_processing.initialize_writers(os.path.join('test', 'test_result', 'semmed_result_console_app.csv'), os.path.join('test', 'test_result', 'progress.csv'))
    assert console_results_writer is not None
    assert progress_writer is not None
    assert console_results_file is not None
    assert progress_file is not None

def test_save_state():
    data_processing.save_state(os.path.join('test', 'test_result', 'progress.csv'), {'sentence_id': 1, 'predicate_id': 1})
    with open(os.path.join('test', 'test_result', 'progress.csv'), 'r') as f:
        last_line = f.readlines()[-1]
    assert last_line == '1,1\n'

def test_load_state():
    state = data_processing.load_state(os.path.join('test', 'test_result', 'progress.csv'))
    assert state == {'sentence_id': 1, 'predicate_id': 1}

def test_process_sentence(mocker, sample_data):
    mock_llama = mocker.MagicMock()
    mocker.patch('src.data_processing.get_llama_result', return_value='Yes')
    mocker.patch('src.data_processing.write_result_to_csv')
    mocker.patch('src.data_processing.write_progress')
    data_processing.process_sentence(mock_llama, 1, 'sentence', [(1, 1, 'predicate')], set(), None, None)
    data_processing.get_llama_result.assert_called_with(mock_llama, "'Is the triple 'predicate' supported by the sentence: 'sentence'?")
    data_processing.write_result_to_csv.assert_called()
    data_processing.write_progress.assert_called()

def test_process_data_and_fact_check(mocker):
    mock_llama = mocker.MagicMock()
    mock_writer = mocker.MagicMock()
    mocker.patch('src.data_processing.load_state', return_value=None)
    mocker.patch('src.data_processing.initialize_writers', return_value=(mock_writer, mock_writer, None, None))
    mocker.patch('src.data_processing.process_sentence')
    data_processing.process_data_and_fact_check(mock_llama, pd.DataFrame(), pd.DataFrame(), os.path.join('test', 'test_result', 'semmed_result_console_app.csv'), os.path.join('test', 'test_result', 'progress.csv'))
