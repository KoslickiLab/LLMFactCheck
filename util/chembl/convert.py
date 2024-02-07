import json
import pandas as pd


def create_csvs(json_path: str, name: str):
    with open(json_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)

        sentence_columns = ["SENTENCE_ID", "PMID", "TYPE", "NUMBER", "SENT_START_INDEX", "SENTENCE",
                            "SECTION_HEADER", "NORMALIZED_SECTION_HEADER", "Column", "Column"]
        sentence_records = []

        triple_columns = ["PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE",
                          "SUBJECT_CUI", "SUBJECT_NAME", "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY",
                          "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE", "OBJECT_NOVELTY",
                          "Column", "Column", "Column"]
        triple_records = []

        for item in data:
            segments = item['p2']['segments'][0]

            subject_data = segments['end']['properties']
            object_data = segments['start']['properties']
            predicate_data = segments['relationship']['properties']

            subject_name = subject_data['name']
            object_name = object_data['name']
            predicate = predicate_data['predicate'].split('biolink:', 1)[1].replace('_', ' ')
            sentence = subject_data['description']
            sentence_id = segments['end']['identity']
            predicate_id = predicate_data['id']

            sentence_records.append({
                "SENTENCE_ID": sentence_id,
                "PMID": None,
                "TYPE": None,
                "NUMBER": None,
                "SENT_START_INDEX": None,
                "SENTENCE": sentence,
                "SECTION_HEADER": None,
                "NORMALIZED_SECTION_HEADER": None,
                "Column": None,
                "Column": None
            })

            triple_records.append({
                "PREDICATION_ID": predicate_id,
                "SENTENCE_ID": sentence_id,
                "PMID": None,
                "PREDICATE": predicate,
                "SUBJECT_CUI": None,
                "SUBJECT_NAME": subject_name,
                "SUBJECT_SEMTYPE": None,
                "SUBJECT_NOVELTY": None,
                "OBJECT_CUI": None,
                "OBJECT_NAME": object_name,
                "OBJECT_SEMTYPE": None,
                "OBJECT_NOVELTY": None,
                "Column": None,
                "Column": None,
                "Column": None
            })

        sentence_df = pd.DataFrame(sentence_records, columns=sentence_columns)
        triple_df = pd.DataFrame(triple_records, columns=triple_columns)

        sentence_df.to_csv(f"{name}_sentence_data.csv", index=False)
        triple_df.to_csv(f"{name}_triple_data.csv", index=False)


create_csvs('~\neo4j_false.json', 'false')
