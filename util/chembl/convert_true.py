import json
import pandas as pd


def create_csvs(json_path: str, name: str):
    with open(json_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)

        sentence_columns = ["SENTENCE_ID", "PMID", "TYPE", "NUMBER", "SENT_START_INDEX", "SENTENCE",
                            "SECTION_HEADER", "NORMALIZED_SECTION_HEADER", "Column", "Column"]
        sentence_records = []

        labeled_columns = ["Predicate ID", "Triple", "Sentence ID", "Sentence", "Question", "Label",
                            "Reference"]
        labeled_records = []
                    #Predicate ID,Triple,Sentence ID,Sentence,Question,Label,Reference

        triple_columns = ["PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE",
                          "SUBJECT_CUI", "SUBJECT_NAME", "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY",
                          "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE", "OBJECT_NOVELTY",
                          "Column", "Column", "Column"]
        triple_records = []
        sentence_id = 0
        n=100
        for item in data:
            segments = item['p3']['segments'][0]

            subject_data = segments['end']['properties']
            object_data = segments['start']['properties']
            predicate_data = segments['relationship']['properties']

            subject_name = subject_data['name']
            object_name = object_data['name']
            predicate = predicate_data['predicate'].split('biolink:', 1)[1].replace('_', ' ')
            sentence = eval(predicate_data['publications_info'])
            print(sentence)
            sentence= sentence[list(sentence.keys())[0]]["sentence"]
            print(sentence)
            sentence_id = sentence_id+1
            predicate_id = predicate_data['id']
            

            labeled_records.append({
                "Predicate ID": predicate_id,
                "Triple": f"{subject_name} {predicate} {object_name}",
                "Sentence ID": sentence_id+n,
                "Sentence": sentence,
                "Question": f"Is the triple \"{subject_name} {predicate} {object_name}\" supported by the sentence: \"{sentence}\"?",
                "Label": False,
                "Reference": None
            })
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
                "SENTENCE_ID": sentence_id+n,
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
            if sentence_id==400: 
             n=-400
        labeled_records_df=pd.DataFrame(labeled_records, columns=labeled_columns)
        sentence_df = pd.DataFrame(sentence_records, columns=sentence_columns)
        triple_df = pd.DataFrame(triple_records, columns=triple_columns)

        labeled_records_df.to_csv(f"{name}_labeled_records.csv", index=False)
        sentence_df.to_csv(f"{name}_sentence_data.csv", index=False)
        triple_df.to_csv(f"{name}_triple_data.csv", index=False)
        

create_csvs('json/neo4j_false.json', 'false')
