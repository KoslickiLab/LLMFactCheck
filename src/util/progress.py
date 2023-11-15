import csv
from typing import Any

PROGRESS_FILE = "result/progress.csv"


def read_progress() -> list[tuple[int, ...]] | list[Any]:
    try:
        with open(PROGRESS_FILE, "r") as file:
            reader = csv.reader(file)
            return [tuple(map(int, row)) for row in reader]
    except FileNotFoundError:
        return []


def write_progress(sentence_id: int, predicate_id: int) -> None:
    progress = read_progress()
    progress.append((sentence_id, predicate_id))

    with open(PROGRESS_FILE, "a+", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(progress)
