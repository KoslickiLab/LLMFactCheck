import os
import argparse
from config import OPENAI_API_KEY
from src.data_processing import read_data_from_files
from src.load_model import load_model
from src.processing import process_data
import debugpy
debugpy.listen(('localhost', 5678))

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

result_folder = "result"
progress_folder = "progress"


def main() -> None:
    """
    Main function to run the Fact-Checking App.
    This function parses command-line arguments,
    reads data from files, loads the language model, and initiates the data processing.
    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="Fact-Checking App")
    parser.add_argument("--model", required=True, choices=['llama', 'gpt_4_0', 'gpt_3_5_turbo'], help="Model to use")
    parser.add_argument("--icl", action='store_true', help="Use In-Context Learning")
    parser.add_argument("--triple_file", required=True, help="Path to the SemMedDB triple file")
    parser.add_argument("--sentence_file", required=True, help="Path to the SemMedDB sentence file")
    args = parser.parse_args()
    triple_data, sentence_data = read_data_from_files(args.triple_file, args.sentence_file)

    model_info = load_model(args.model, args.icl)

    icl_suffix = '_icl' if args.icl else ''
    result_file_name = f"{args.model}{icl_suffix}_semmed_result.csv"
    progress_file_name = f"{args.model}{icl_suffix}_progress.csv"

    process_data(model_info, args.model, args.icl, triple_data, sentence_data,
                 os.path.join(result_folder, result_file_name),
                 os.path.join(result_folder, progress_folder, progress_file_name))


if __name__ == "__main__":
    main()
