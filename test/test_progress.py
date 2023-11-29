import pytest
from unittest.mock import mock_open, call, MagicMock
from src.progress import read_progress, write_progress, PROGRESS_FILE

BUILTINS_OPEN = 'builtins.open'

@pytest.fixture
def mock_file(mocker):
    return mocker.patch(BUILTINS_OPEN, new_callable=mock_open)

def test_read_progress(mocker, mock_file):
    mock_csv = mocker.patch('csv.reader')
    mock_csv.return_value = iter([(1, 2), (3, 4)])
    result = read_progress()
    mock_csv.assert_called_once()
    assert result == [(1, 2), (3, 4)]

def test_read_progress_file_not_found(mocker):
    mock_file = mocker.patch(BUILTINS_OPEN)
    mock_file.side_effect = FileNotFoundError()
    result = read_progress()
    mock_file.assert_called_once_with(PROGRESS_FILE, "r")
    assert result == []

def test_write_progress(mocker):
    mocker.patch('src.progress.read_progress', return_value=[])
    mock_file = mocker.patch(BUILTINS_OPEN, new_callable=mock_open)
    mock_csv = mocker.patch('csv.writer')
    mock_writer = MagicMock()
    mock_csv.return_value = mock_writer
    write_progress(5, 6)
    mock_file.assert_called_once_with(PROGRESS_FILE, "a+", newline="")
    mock_writer.writerows.assert_called_once_with([(5, 6)])
