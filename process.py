import json
import csv
import ast  # Import the ast module for safely evaluating strings as Python expressions
import pandas as pd
# File paths
edges_file_path = 'kg2c-2.8.4-edges.jsonl'
nodes_file_path = 'kg2c-2.8.4-nodes.jsonl'
output_csv_path = 'output_filtered.csv'

# Load all nodes into a dictionary for quick access by ID
nodes = {}
with open(nodes_file_path, 'r') as nodes_file:
    for line in nodes_file:
        node_data = json.loads(line)
        # Get the name or the first alternative name if the primary name is absent
        name = node_data.get('name') or (node_data.get('all_names')[0] if 'all_names' in node_data and node_data['all_names'] else "Unknown")
        nodes[node_data['id']] = name

# Process edges that meet the criteria
with open(edges_file_path, 'r') as edges_file, open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:
    csv_writer = csv.writer(output_file)
    csv_writer.writerow(['ID', 'Fact', 'Source', 'Template', 'Reference', 'Name'])

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
    sentence_id=0
    for line in edges_file:
        edge = json.loads(line)
        
        # Filter based on the knowledge source and retrieve the sentence
        if edge.get('primary_knowledge_source') == 'infores:semmeddb':
            publications_info_raw = edge.get('publications_info', '{}')
            try:
                # Use ast.literal_eval to safely evaluate the string as a Python dictionary
                publications_info = ast.literal_eval(publications_info_raw)
            except ValueError as e:
                print(f"Error parsing publications_info: {publications_info_raw} with error: {e}")
                publications_info = {}

            # Extracting the first available sentence from publications_info
            sentence = next((info.get('sentence', '') for info in publications_info.values()), '')

            # Use names instead of IDs where possible
            subject_name = nodes.get(edge['subject'], edge['subject'])
            predicate_name = nodes.get(edge['predicate'], edge['predicate'])
            object_name = nodes.get(edge['object'], edge['object'])

            # Construct the Fact
            fact = f"{subject_name} {predicate_name} {object_name}"

            # Write to CSV
            csv_writer.writerow([edge['id'], fact, sentence, '', '', ''])


            labeled_records.append({
                "Predicate ID": edge['id'],
                "Triple": f"{subject_name} {predicate_name} {object_name}",
                "Sentence ID": sentence_id,
                "Sentence": sentence,
                "Question": f"Is the triple \"{subject_name} {predicate_name} {object_name}\" supported by the sentence: \"{sentence}\"?",
                "Label": None,
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
                "PREDICATION_ID": edge['id'],
                "SENTENCE_ID": sentence_id,
                "PMID": None,
                "PREDICATE": predicate_name,
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
            sentence_id=sentence_id+1
            #print(labeled_records)
            #print("__")
            #print(sentence_records)
            #print("__")
            #print(triple_records)
            #print("__")
    labeled_records_df=pd.DataFrame(labeled_records, columns=labeled_columns)
    sentence_df = pd.DataFrame(sentence_records, columns=sentence_columns)
    triple_df = pd.DataFrame(triple_records, columns=triple_columns)

    labeled_records_df.to_csv(f"{name}_labeled_records.csv", index=False)
    sentence_df.to_csv(f"{name}_sentence_data.csv", index=False)
    triple_df.to_csv(f"{name}_triple_data.csv", index=False)
    

print("Filtered CSV file has been generated successfully.")
