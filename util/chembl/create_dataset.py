import json
import csv
import os


def create_dataset_from_json(json_file_name: str, dataset_name: str):
    """
    Creates a CSV file with data retrieved from a json file

    This function reads data from a json file and creates a CSV file to which it writes the data from the json.
    The created dataset is saved to the data folder, which is located in the project root.

    Parameters
    ----------
    json_file_name : str
        Name of the JSON file that was received from the neo4j service. The file must be in the root of the project
    dataset_name : str
        Name of the dataset to be created.

    Returns
    -------
    None

    Raises
    -------
    FileNotFoundError
        If the json file is not found.
    json.JSONDecodeError
        If JSON decoding fails.
    """
    try:
        json_path = os.path.abspath(json_file_name + '.json')
        print(json_path)

        if not os.path.exists(json_path):
            raise FileNotFoundError('JSON file not found')

        path_to_save_df = os.path.join(os.getcwd(), 'data', f'{dataset_name}.csv')

        with open(path_to_save_df, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Predicate ID', 'Triple', 'Sentence ID', 'Sentence', 'Question', 'Label', 'Reference'])
            write_data(json_path, writer)

    except FileNotFoundError as e:
        print(f"Error: {e}. File not found.")
    except json.JSONDecodeError as e:
        print(f"Error: {e}. JSON decoding failed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def write_data(json_path: str, writer: csv.writer):
    with open(json_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)
        for item in data:
            segments = item['p']['segments'][0]

            subject_data = segments['end']['properties']
            object_data = segments['start']['properties']
            predicate_data = segments['relationship']['properties']

            subject_name = subject_data['name']
            object_name = object_data['name']
            predicate = predicate_data['predicate'].split('biolink:', 1)[1].replace('_', ' ')
            sentence = subject_data['description']
            publications = object_data['publications'][0] if 'publications' in object_data else ''
            sentence_id = segments['end']['identity']

            triple = generate_triple(subject_name, predicate, object_name)
            question = generate_question(triple, sentence)

            writer.writerow([
                predicate_data['id'],
                triple,
                sentence_id,
                sentence,
                question,
                "True",
                publications
            ])


def generate_triple(subject_name: str, predicate: str, object_name: str):
    return f"{subject_name} {predicate} {object_name}"


def generate_question(triple: str, sentence: str):
    return f"Is the triple {triple} supported by the sentence {sentence}"