import json
import csv
import ast  # Import the ast module for safely evaluating strings as Python expressions
import pandas as pd
import logging
# This file also defines a class KGDataExtractor with similar functionality but includes additional features:

# Loading Nodes with Equivalent Curies: In addition to loading nodes, it builds a map of equivalent curies to node names.
# Processing Edges with Sentence Extraction: Similar to the previous file, but it includes a method to extract sentences from the edge's publications_info and uses equivalent curies to get node names if the primary ID is not found.
# Saving DataFrames: Similar to the previous file, it saves the records to separate CSV files.


class KGDataExtractor:
    """
    A class for extracting and filtering knowledge graph data from JSONL files and exporting results to CSV.
    """

    def __init__(self, edges_file_path: str, nodes_file_path: str, output_csv_path: str, base_name: str = "output"):
        """
        Initialize the data extractor.

        Args:
            edges_file_path (str): Path to the edges JSONL file.
            nodes_file_path (str): Path to the nodes JSONL file.
            output_csv_path (str): Path to the main filtered output CSV file.
            base_name (str): Base name for the auxiliary CSV files.
        """
        self.edges_file_path = edges_file_path
        self.nodes_file_path = nodes_file_path
        self.output_csv_path = output_csv_path
        self.base_name = base_name

        self.nodes = {}
        self.labeled_records = []
        self.sentence_records = []
        self.triple_records = []

    def run(self):
        """Execute the data loading, filtering, and saving process."""
        self._load_nodes()
        self._process_edges()
        self._save_dataframes()
        logging.info("Filtered CSV file has been generated successfully.")

    def _load_nodes(self):
        """Load all nodes into a dictionary for quick access by ID."""
        with open(self.nodes_file_path, 'r', encoding='utf-8') as nodes_file:
            for line in nodes_file:
                node_data = json.loads(line)
                # Get the name or the first alternative name if the primary name is absent
                name = node_data.get('name') or (
                    node_data.get('all_names')[0] if 'all_names' in node_data and node_data['all_names'] else "Unknown"
                )
                self.nodes[node_data['id']] = name

    def _process_edges(self):
        """Process edges that meet the criteria and write the main CSV file."""
        with open(self.edges_file_path, 'r', encoding='utf-8') as edges_file, \
             open(self.output_csv_path, 'w', newline='', encoding='utf-8') as output_file:

            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['ID', 'Fact', 'Source', 'Template', 'Reference', 'Name'])

            sentence_id = 0
            for line in edges_file:
                edge = json.loads(line)
                
                # Filter based on the knowledge source and retrieve the sentence
                if edge.get('primary_knowledge_source') == 'infores:semmeddb':
                    publications_info_raw = edge.get('publications_info', '{}')
                    try:
                        # Use ast.literal_eval to safely evaluate the string as a Python dictionary
                        publications_info = ast.literal_eval(publications_info_raw)
                    except ValueError as e:
                        logging.info(f"Error parsing publications_info: {publications_info_raw} with error: {e}")
                        publications_info = {}

                    # Extracting the first available sentence from publications_info
                    sentence = next((info.get('sentence', '') for info in publications_info.values()), '')

                    # Use names instead of IDs where possible
                    subject_name = self.nodes.get(edge['subject'], edge['subject'])
                    predicate_name = self.nodes.get(edge['predicate'], edge['predicate'])
                    object_name = self.nodes.get(edge['object'], edge['object'])

                    # Construct the Fact
                    fact = f"{subject_name} {predicate_name} {object_name}"

                    # Write to main CSV
                    csv_writer.writerow([edge['id'], fact, sentence, '', '', ''])

                    self._append_records(edge, sentence_id, sentence, subject_name, predicate_name, object_name)
                    sentence_id += 1

    def _append_records(self, edge, sentence_id, sentence, subject_name, predicate_name, object_name):
        """Append records to labeled, sentence and triple lists."""
        self.labeled_records.append({
            "Predicate ID": edge['id'],
            "Triple": f"{subject_name} {predicate_name} {object_name}",
            "Sentence ID": sentence_id,
            "Sentence": sentence,
            "Question": f'Is the triple "{subject_name} {predicate_name} {object_name}" supported by the sentence: "{sentence}"?',
            "Label": None,
            "Reference": None
        })

        self.sentence_records.append({
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

        self.triple_records.append({
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

    def _save_dataframes(self):
        """Save the DataFrames to CSV files."""
        sentence_columns = [
            "SENTENCE_ID", "PMID", "TYPE", "NUMBER", "SENT_START_INDEX", "SENTENCE",
            "SECTION_HEADER", "NORMALIZED_SECTION_HEADER", "Column", "Column"
        ]

        labeled_columns = [
            "Predicate ID", "Triple", "Sentence ID", "Sentence", "Question", "Label", "Reference"
        ]

        triple_columns = [
            "PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE",
            "SUBJECT_CUI", "SUBJECT_NAME", "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY",
            "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE", "OBJECT_NOVELTY",
            "Column", "Column", "Column"
        ]

        labeled_records_df = pd.DataFrame(self.labeled_records, columns=labeled_columns)
        sentence_df = pd.DataFrame(self.sentence_records, columns=sentence_columns)
        triple_df = pd.DataFrame(self.triple_records, columns=triple_columns)

        labeled_records_df.to_csv(f"{self.base_name}_labeled_records.csv", index=False)
        sentence_df.to_csv(f"{self.base_name}_sentence_data.csv", index=False)
        triple_df.to_csv(f"{self.base_name}_triple_data.csv", index=False)


if __name__ == "__main__":
    extractor = KGDataExtractor(
        edges_file_path='kg2c-2.8.4-edges.jsonl',
        nodes_file_path='kg2c-2.8.4-nodes.jsonl',
        output_csv_path='output_filtered.csv',
        base_name='output'
    )
    extractor.run()
