import pandas as pd
import pytest
from src.triple_processing import process_triple_row


@pytest.fixture
def sample_row():
    data = {
        "SENTENCE_ID": [1],
        "PREDICATION_ID": [101],
        "PREDICATE": ['"_isa_"'],
        "SUBJECT_NAME": ['"_Cat_"'],
        "OBJECT_NAME": ['"_Animal_"']
    }
    return pd.DataFrame(data).iloc[0]


def test_process_triple_row(sample_row):
    sentence_id, predicate_id, triple = process_triple_row(sample_row)
    assert sentence_id == 1
    assert predicate_id == 101
    assert triple == 'Cat is a Animal'
