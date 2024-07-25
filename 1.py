import json
import csv
import ast  # Import the ast module

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

    for line in edges_file:
        edge = json.loads(line)
        
        # Filter based on the knowledge source
        if edge.get('primary_knowledge_source') == 'infores:semmeddb':
            publications_info_raw = edge.get('publications_info', '{}')
            try:
                # Safely evaluate the string to a Python dictionary
                publications_info = ast.literal_eval(publications_info_raw)
            except (SyntaxError, ValueError) as e:
                # Handle errors in literal evaluation
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
            # print([edge['id'], fact, sentence, '', '', ''])

print("Filtered CSV file has been generated successfully.")
