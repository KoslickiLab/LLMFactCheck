import sys
import os

sys.path.append("..")

import argparse
from src.util.data_processing import read_data_from_files, process_data_and_fact_check
from src.util.llama_interaction import load_llama_model

RESULT_FILE = os.path.abspath("result/semmed_result_console_app.csv")


def main():
    parser = argparse.ArgumentParser(description="LLM Fact-Checking App")
    parser.add_argument("--predication_file", required=True, help="Path to the semmeddb predicate file")
    parser.add_argument("--sentence_file", required=True, help="Path to the semmeddb sentence file")

    args = parser.parse_args()

    predication_file = args.predication_file
    sentence_file = args.sentence_file

    lcpp_llm = load_llama_model()
    predication_data, sentence_data = read_data_from_files(predication_file, sentence_file)
    process_data_and_fact_check(lcpp_llm, predication_data, sentence_data, RESULT_FILE)


if __name__ == "__main__":
    main()
