import json
import csv
import ast
import logging  # Import the ast module for safely evaluating strings as Python expressions
import pandas as pd

# This file defines a class KGDataExtractor that loads, filters, and exports knowledge graph data from JSONL files (nodes and edges) to CSV files. It extracts triples (subject-predicate-object) from edges, matches them with sentences, and stores results in multiple CSV outputs.

class KGDataExtractor:
    """
    A class to load, filter, and export knowledge graph edges and nodes data to CSV files.
    It extracts triples from edges, matches them with sentences, and stores results in multiple CSV outputs.
    """

    def __init__(self, edges_file_path: str, nodes_file_path: str, output_csv_path: str, base_name: str = "output"):
        """
        Initialize the data extractor with given file paths.

        Args:
            edges_file_path (str): The path to the edges .jsonl file.
            nodes_file_path (str): The path to the nodes .jsonl file.
            output_csv_path (str): The path to the main filtered output CSV file.
            base_name (str): Base name for the generated CSV files. Default is "output".
        """
        self.edges_file_path = edges_file_path
        self.nodes_file_path = nodes_file_path
        self.output_csv_path = output_csv_path
        self.base_name = base_name

        self.nodes = {}
        self.equivalent_curies_map = {}
        self.labeled_records = []
        self.sentence_records = []
        self.triple_records = []

    def run(self):
        """Run the data extraction and filtering process."""
        self._load_nodes()
        self._process_edges()
        self._save_dataframes()
        logging.info("Filtered CSV file has been generated successfully.")

    def _load_nodes(self):
        """Load nodes from the specified file, building a map of IDs to names and equivalent curies."""
        with open(self.nodes_file_path, 'r', encoding='utf-8') as nodes_file:
            for line in nodes_file:
                node_data = json.loads(line)
                name = node_data.get('name') or (
                    node_data.get('all_names')[0] if 'all_names' in node_data and node_data['all_names'] else "Unknown"
                )
                self.nodes[node_data['id']] = name
                for curie in node_data.get('equivalent_curies', []):
                    self.equivalent_curies_map[curie] = name

    def _process_edges(self):
        """Process edges that meet the criteria, write to the main output CSV, and populate records."""
        with open(self.edges_file_path, 'r', encoding='utf-8') as edges_file, \
             open(self.output_csv_path, 'w', newline='', encoding='utf-8') as output_file:

            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['ID', 'Fact', 'Source', 'Template', 'Reference', 'Name'])

            sentence_id = 0
            for line in edges_file:
                edge = json.loads(line)

                # Filter based on the knowledge source and retrieve the sentence
                if edge.get('primary_knowledge_source') == 'infores:semmeddb':
                    sentence = self._extract_sentence(edge)
                    subject_name, predicate_name, object_name = self._get_names(edge)

                    # Construct the Fact
                    fact = f"{subject_name} {predicate_name} {object_name}"

                    # Write to the main CSV file
                    csv_writer.writerow([edge['id'], fact, sentence, '', '', ''])

                    # Append to labeled_records
                    self.labeled_records.append({
                        "Predicate ID": edge['id'],
                        "Triple": fact,
                        "Sentence ID": sentence_id,
                        "Sentence": sentence,
                        "Question": f'Is the triple "{fact}" supported by the sentence: "{sentence}"?',
                        "Label": None,
                        "Reference": None
                    })

                    # Append to sentence_records
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

                    # Append to triple_records
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
                    sentence_id += 1

    def _extract_sentence(self, edge) -> str:
        """Extract the first available sentence from the edge's publications_info."""
        publications_info_raw = edge.get('publications_info', '{}')
        try:
            publications_info = ast.literal_eval(publications_info_raw)
        except ValueError as e:
            logging.info(f"Error parsing publications_info: {publications_info_raw} with error: {e}")
            publications_info = {}

        return next((info.get('sentence', '') for info in publications_info.values()), '')

    def _get_names(self, edge):
        """Get subject, predicate, and object names using nodes or equivalent curies."""
        subject_name = self.nodes.get(edge['subject'], self.equivalent_curies_map.get(edge['subject'], edge['subject']))
        object_name = self.nodes.get(edge['object'], self.equivalent_curies_map.get(edge['object'], edge['object']))
        predicate_name = self.nodes.get(edge['predicate'], self.equivalent_curies_map.get(edge['predicate'], edge['predicate']))
        return subject_name, predicate_name, object_name

    def _save_dataframes(self):
        """Save labeled_records, sentence_records, and triple_records to separate CSV files."""
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
