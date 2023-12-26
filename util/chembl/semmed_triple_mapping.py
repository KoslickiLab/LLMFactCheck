# This code processes the data from the semmed_triple_data.csv file,
# creates a new 'TRIPLE' column from this data, and then filters this data
# to select only those triples that match the predicates specified in the predicate-remap.yaml file.
# As a result, only those triples from SemMedDB that match the predicates from the yaml file are displayed,
# and are also written to the filtered_triple_data.csv file in the project data folder
# yaml from https://github.com/RTXteam/RTX-KG2/blob/master/predicate-remap.yaml

import os
import sys
import pandas as pd
import yaml
from src.triple_processing import process_triple_row

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

current_dir = os.path.dirname(os.path.realpath(__file__))

predicate_file_path = os.path.join(current_dir, '..', '..', 'data', 'predicate-remap.yaml')

with open(predicate_file_path, 'r') as file:
    predicate_mapping_raw = yaml.safe_load(file)


predicate_mapping = {key.replace('_', ' '): value if key != "isa" else "is a" for key, value in
                     predicate_mapping_raw.items()}

data_file_path = os.path.join(current_dir, '..', '..', 'data', 'semmed_triple_data.csv')
semmed_data = pd.read_csv(data_file_path)

semmed_data.columns = [
    "PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE", "SUBJECT_CUI", "SUBJECT_NAME",
    "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY", "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE",
    "OBJECT_NOVELTY", "Column", "Column", "Column"
]

semmed_data['PREDICATE'] = semmed_data['PREDICATE'].str.replace('_', ' ').str.lower()
semmed_data['PREDICATE'] = semmed_data['PREDICATE'].apply(lambda x: "is a" if x == "isa" else x)

semmed_data['TRIPLE'] = semmed_data.apply(lambda row: process_triple_row(row)[2], axis=1)

new_predicate_mapping = {key.split(':')[1]: value for key, value in predicate_mapping.items()}

filtered_data = semmed_data[semmed_data['PREDICATE'].isin(new_predicate_mapping.keys())]

print(filtered_data.head())

filtered_data = (filtered_data[['PREDICATION_ID', 'SENTENCE_ID', 'TRIPLE']].rename
                 (columns={'PREDICATION_ID': 'Predicate ID', 'SENTENCE_ID': 'Sentence ID', 'TRIPLE': 'Triple'}))

filtered_data = filtered_data.reindex(columns=['Predicate ID', 'Triple', 'Sentence ID'])

filtered_data.to_csv(os.path.join('..', '..', 'data', 'filtered_triple_data.csv'), index=False)
