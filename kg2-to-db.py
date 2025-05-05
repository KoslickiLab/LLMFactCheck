import json
import ast
import psycopg2
from psycopg2.extras import execute_batch

# Database connection details
conn = psycopg2.connect(
    dbname="biomedical",
    user="postgres",
    password=",
    host="",
    port="5432"
)
cursor = conn.cursor()

# File paths
edges_file_path = 'kg2c-2.8.4-edges.jsonl'
nodes_file_path = 'kg2c-2.8.4-nodes.jsonl'

# Load all nodes into a dictionary for quick access by ID
nodes = {}
equivalent_curies_map = {}
with open(nodes_file_path, 'r') as nodes_file:
    for line in nodes_file:
        node_data = json.loads(line)
        name = node_data.get('name') or (node_data.get('all_names')[0] if 'all_names' in node_data and node_data['all_names'] else "Unknown")
        nodes[node_data['id']] = name
        for curie in node_data.get('equivalent_curies', []):
            equivalent_curies_map[curie] = name 

# Prepare batch insertion
batch_size = 10000  # Adjust this size according to your available memory
insert_data = []

with open(edges_file_path, 'r') as edges_file:
    for line in edges_file:
        edge = json.loads(line)
        
        if edge.get('primary_knowledge_source') == 'infores:semmeddb':
            publications_info_raw = edge.get('publications_info', '{}')
            try:
                publications_info = ast.literal_eval(publications_info_raw)
            except ValueError as e:
                print(f"Error parsing publications_info: {publications_info_raw} with error: {e}")
                publications_info = {}

            # Extract all sentences from publications_info
            sentences = []
            for info in publications_info.values():
                if 'sentence' in info and info['sentence']:
                    sentences.append(info['sentence'])
            
            # If no sentences were found, add an empty one to ensure the triple is still recorded
            if not sentences:
                sentences = ['']
                
            subject_name = nodes.get(edge['subject'], equivalent_curies_map.get(edge['subject'], edge['subject']))
            object_name = nodes.get(edge['object'], equivalent_curies_map.get(edge['object'], edge['object']))
            predicate_name = nodes.get(edge['predicate'], equivalent_curies_map.get(edge['predicate'], edge['predicate']))
            fact = f"{subject_name} {predicate_name} {object_name}"

            # Add each sentence as a separate row with the same triple
            for sentence in sentences:
                insert_data.append((edge['id'], fact, sentence))

            if len(insert_data) >= batch_size:
                execute_batch(
                    cursor,
                    """
                    INSERT INTO public."tblbiomedicalfactcheck_new" ("nodeDataID", "triple", "sentence")
                    VALUES (%s, %s, %s)
                    """,
                    insert_data
                )
                conn.commit()
                insert_data.clear()

# Insert remaining data
if insert_data:
    execute_batch(
        cursor,
        """
        INSERT INTO public."tblbiomedicalfactcheck_new" ("nodeDataID", "triple", "sentence")
        VALUES (%s, %s, %s)
        """,
        insert_data
    )
    conn.commit()

# Clean up
cursor.close()
conn.close()

print("Data has been inserted into the database successfully.")
