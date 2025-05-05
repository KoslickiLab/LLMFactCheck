import json
import csv
import ast
import logging
import os
from typing import Dict, Any, Optional, List
import pandas as pd

# This file defines a class KGDataExtractor that loads and filters knowledge graph data from JSONL files (nodes and edges), then writes the filtered results into CSV files. It extracts triples (subject-predicate-object) from edges, links them with sentences from publications_info, and produces several CSV outputs.

class KGDataExtractor:
    """
    A class to load and filter knowledge graph data from JSONL files (nodes and edges),
    then write the filtered results into CSV files. It extracts triples (subject-predicate-object)
    from edges, links them with sentences from publications_info, and produces several CSV outputs.
    """

    def __init__(self, 
                 nodes_file_path: str,
                 edges_file_path: str,
                 output_csv_path: str,
                 base_name: str = "output"):
        """
        Initialize the KGDataExtractor.

        Args:
            nodes_file_path (str): Path to the nodes JSONL file.
            edges_file_path (str): Path to the edges JSONL file.
            output_csv_path (str): Path to the main filtered output CSV file.
            base_name (str): Base name for additional CSV files for labeled_records,
                             sentence_data and triple_data. Default is "output".
        """
        self.nodes_file_path = nodes_file_path
        self.edges_file_path = edges_file_path
        self.output_csv_path = output_csv_path
        self.base_name = base_name

        self.nodes = {}
        self.equivalent_curies_map = {}

    def run(self):
        """Execute the extraction and filtering process."""
        self._load_nodes()
        self._process_edges()

    def _load_nodes(self) -> None:
        """
        Load all nodes into a dictionary for quick access by ID,
        and build a map of equivalent CURIEs to names.
        """
        with open(self.nodes_file_path, 'r', encoding='utf-8') as nodes_file:
            for line in nodes_file:
                node_data = json.loads(line)
                name = self._get_node_name(node_data)
                self.nodes[node_data['id']] = name

                # Map equivalent curies to the primary name
                for curie in node_data.get('equivalent_curies', []):
                    self.equivalent_curies_map[curie] = name

    @staticmethod
    def _get_node_name(node_data: Dict[str, Any]) -> str:
        """
        Get the name of a node. If 'name' is not present, 
        try using the first element of 'all_names'.
        If none found, return "Unknown".
        """
        if node_data.get('name'):
            return node_data['name']
        elif node_data.get('all_names'):
            return node_data['all_names'][0]
        return "Unknown"

    def _process_edges(self) -> None:
        """
        Process edges that meet the criteria and write the filtered results.
        This method:
         - Filters edges by 'primary_knowledge_source' == 'infores:semmeddb'
         - Extracts a sentence from publications_info
         - Maps subject, predicate, object to their respective names
         - Writes a main CSV file with filtered edges
         - Creates and saves three additional CSV files: labeled_records, sentence_data, triple_data
        """
        with open(self.edges_file_path, 'r', encoding='utf-8') as edges_file, \
             open(self.output_csv_path, 'w', newline='', encoding='utf-8') as output_file:

            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['ID', 'Fact', 'Source', 'Template', 'Reference', 'Name'])

            labeled_records = []
            sentence_records = []
            triple_records = []

            sentence_columns = [
                "SENTENCE_ID", "PMID", "TYPE", "NUMBER", "SENT_START_INDEX", "SENTENCE",
                "SECTION_HEADER", "NORMALIZED_SECTION_HEADER", "Column", "Column"
            ]

            labeled_columns = [
                "Predicate ID", "Triple", "Sentence ID", "Sentence", "Question", "Label",
                "Reference"
            ]

            triple_columns = [
                "PREDICATION_ID", "SENTENCE_ID", "PMID", "PREDICATE",
                "SUBJECT_CUI", "SUBJECT_NAME", "SUBJECT_SEMTYPE", "SUBJECT_NOVELTY",
                "OBJECT_CUI", "OBJECT_NAME", "OBJECT_SEMTYPE", "OBJECT_NOVELTY",
                "Column", "Column", "Column"
            ]

            sentence_id = 0

            for line in edges_file:
                edge = json.loads(line)

                # Check the primary knowledge source
                if edge.get('primary_knowledge_source') == 'infores:semmeddb':
                    # Extract the first available sentence from publications_info
                    sentence = self._extract_sentence(edge.get('publications_info', '{}'))

                    subject_name, predicate_name, object_name = self._get_triple_names(edge)
                    fact = f"{subject_name} {predicate_name} {object_name}"

                    # Write to the main output CSV
                    csv_writer.writerow([edge['id'], fact, sentence, '', '', ''])

                    # Prepare labeled_record
                    labeled_records.append({
                        "Predicate ID": edge['id'],
                        "Triple": fact,
                        "Sentence ID": sentence_id,
                        "Sentence": sentence,
                        "Question": f'Is the triple "{fact}" supported by the sentence: "{sentence}"?',
                        "Label": None,
                        "Reference": None
                    })

                    # Prepare sentence record
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

                    # Prepare triple record
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
                    sentence_id += 1

            # Create DataFrames
            labeled_records_df = pd.DataFrame(labeled_records, columns=labeled_columns)
            sentence_df = pd.DataFrame(sentence_records, columns=sentence_columns)
            triple_df = pd.DataFrame(triple_records, columns=triple_columns)

            # Save additional CSV files
            labeled_records_df.to_csv(f"{self.base_name}_labeled_records.csv", index=False)
            sentence_df.to_csv(f"{self.base_name}_sentence_data.csv", index=False)
            triple_df.to_csv(f"{self.base_name}_triple_data.csv", index=False)

        logging.info("Filtered CSV file has been generated successfully.")

    def _extract_sentence(self, publications_info_raw: str) -> str:
        """
        Extract the first available sentence from the publications_info field.
        If parsing fails or no sentence found, returns an empty string.
        """
        try:
            publications_info = ast.literal_eval(publications_info_raw)
        except ValueError as e:
            logging.info(f"Error parsing publications_info: {publications_info_raw} with error: {e}")
            return ''

        # Extract the first sentence found
        return next((info.get('sentence', '') for info in publications_info.values()), '')

    def _get_triple_names(self, edge: Dict[str, Any]) -> tuple:
        """
        Get human-readable names for subject, predicate, object from the edge,
        using nodes or equivalent_curies_map.
        """
        subject_name = self.nodes.get(edge['subject'], self.equivalent_curies_map.get(edge['subject'], edge['subject']))
        object_name = self.nodes.get(edge['object'], self.equivalent_curies_map.get(edge['object'], edge['object']))
        predicate_name = self.nodes.get(edge['predicate'], self.equivalent_curies_map.get(edge['predicate'], edge['predicate']))
        return subject_name, predicate_name, object_name


if __name__ == "__main__":
    # Приклад використання
    extractor = KGDataExtractor(
        nodes_file_path='kg2c-2.8.4-nodes.jsonl',
        edges_file_path='kg2c-2.8.4-edges.jsonl',
        output_csv_path='output_filtered.csv',
        base_name='output'
    )
    extractor.run()
