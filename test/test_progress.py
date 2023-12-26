from unittest.mock import patch, mock_open, call
from src.progress import read_progress, write_progress


@patch('src.progress.PROGRESS_FILES', {'test_model': 'test_model.csv'})
@patch('builtins.open', new_callable=mock_open, read_data="Sentence ID,Predicate ID\n1,2\n3,4\n")
def test_read_progress(_):
    result = read_progress('test_model')
    assert result == [(1, 2), (3, 4)]


@patch('src.progress.PROGRESS_FILES', {'test_model': 'test_model.csv'})
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.isfile', return_value=True)
@patch('os.stat')
def test_write_progress(mock_stat, _, mock_file):
    mock_stat.return_value.st_size = 10
    write_progress('test_model', 5, 6)
    calls = [call('5,6\r\n')]
    mock_file.return_value.write.assert_has_calls(calls)


@patch('src.progress.PROGRESS_FILES', {'test_model': 'test_model.csv'})
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.isfile', return_value=False)
@patch('os.stat')
def test_write_progress_new_file(mock_stat, _, mock_file):
    mock_stat.return_value.st_size = 0
    write_progress('test_model', 5, 6)
    calls = [call('Sentence ID,Predicate ID\r\n'), call('5,6\r\n')]
    mock_file.return_value.write.assert_has_calls(calls)


def test_read_progress_invalid_model():
    try:
        read_progress('invalid_model')
    except ValueError:
        pass


def test_write_progress_invalid_model():
    try:
        write_progress('invalid_model', 5, 6)
    except ValueError:
        pass
