import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
from src.util.data_processing import read_data_from_files, process_data_and_fact_check
from src.util.llama_interaction import load_llama_model


result_folder = "result"
RESULT_FILE = os.path.abspath(os.path.join(result_folder, "semmed_result_console_app.csv"))
PROGRESS_FILE = os.path.abspath(os.path.join(result_folder, "progress.csv"))


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="LLM Fact-Checking App")
    parser.add_argument("--predication_file", required=True, help="Path to the semmeddb predicate file")
    parser.add_argument("--sentence_file", required=True, help="Path to the semmeddb sentence file")

    args: argparse.Namespace = parser.parse_args()

    predication_file: str = args.predication_file
    sentence_file: str = args.sentence_file

    lcpp_llm = load_llama_model()
    predication_data, sentence_data = read_data_from_files(predication_file, sentence_file)

    process_data_and_fact_check(
        lcpp_llm, predication_data, sentence_data, RESULT_FILE, PROGRESS_FILE
    )


if __name__ == "__main__":
    main()
