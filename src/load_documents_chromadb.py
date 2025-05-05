import ast
import json
import logging

import openai
from decouple import config
from dotenv import load_dotenv

from load_model import ChromaDBInitializer
from logger_config import Logger

#Description:
#The code snippet defines a class FileReader that handles reading and processing of files.

class FileReader:
    """Handles reading and processing of files."""

    @staticmethod
    def count_lines(file_path):
        with open(file_path, "r") as f:
            return sum(1 for _ in f)

    @staticmethod
    def read_lines(file_path):
        with open(file_path, "r") as f:
            for line in f:
                yield line


class NodeProcessor:
    """Processes node data from the nodes file."""

    def __init__(self, nodes_file_path, sampling_rate):
        self.nodes_file_path = nodes_file_path
        self.sampling_rate = sampling_rate
        self.nodes = {}
        self.equivalent_curies_map = {}

    def load_nodes(self):
        total_nodes = FileReader.count_lines(self.nodes_file_path)
        max_nodes = int(total_nodes * self.sampling_rate)
        logging.info(
            f"Processing first {max_nodes} nodes ({self.sampling_rate * 100:.2f}% of total)."
        )

        try:
            for line_number, line in enumerate(
                FileReader.read_lines(self.nodes_file_path), 1
            ):
                node_data = json.loads(line)
                name = node_data.get("name") or (
                    node_data.get("all_names")[0]
                    if "all_names" in node_data and node_data["all_names"]
                    else "Unknown"
                )
                self.nodes[node_data["id"]] = name
                for curie in node_data.get("equivalent_curies", []):
                    self.equivalent_curies_map[curie] = name

                if line_number % 500000 == 0:
                    logging.info(f"Processed {line_number} nodes.")

            logging.info(f"Loaded {len(self.nodes)} nodes into memory.")
        except Exception as e:
            logging.error(f"Error loading nodes: {e}")
            exit(1)


class EdgeProcessor:
    """Processes edge data and prepares documents for indexing."""

    def __init__(self, edges_file_path, nodes, equivalent_curies_map, sampling_rate):
        self.edges_file_path = edges_file_path
        self.nodes = nodes
        self.equivalent_curies_map = equivalent_curies_map
        self.sampling_rate = sampling_rate
        self.documents = []

    def process_edges(self):
        total_edges = FileReader.count_lines(self.edges_file_path)
        max_edges = int(total_edges * self.sampling_rate)
        logging.info(
            f"Processing first {max_edges} edges ({self.sampling_rate * 100:.2f}% of total)."
        )

        try:
            for line_number, line in enumerate(
                FileReader.read_lines(self.edges_file_path), 1
            ):
                edge = json.loads(line)

                if edge.get("primary_knowledge_source") != "infores:semmeddb":
                    publications_info_raw = edge.get("publications_info", "{}")
                    try:
                        publications_info = ast.literal_eval(publications_info_raw)
                    except ValueError as e:
                        logging.error(
                            f"Error parsing publications_info: {publications_info_raw} with error: {e}"
                        )
                        publications_info = {}

                    sentence = next(
                        (
                            info.get("sentence", "")
                            for info in publications_info.values()
                        ),
                        "",
                    )
                    subject_name = self.nodes.get(
                        edge["subject"],
                        self.equivalent_curies_map.get(
                            edge["subject"], edge["subject"]
                        ),
                    )
                    object_name = self.nodes.get(
                        edge["object"],
                        self.equivalent_curies_map.get(edge["object"], edge["object"]),
                    )
                    predicate_name = self.nodes.get(
                        edge["predicate"],
                        self.equivalent_curies_map.get(
                            edge["predicate"], edge["predicate"]
                        ),
                    )
                    fact = f"{subject_name} {predicate_name} {object_name}"
                    doc_text = f"Sentence: {sentence}\nTriple: {fact}"

                    self.documents.append({"id": edge["id"], "text": doc_text})

                    if len(self.documents) > 200000:
                        break

                if line_number % 500000 == 0:
                    logging.info(f"Processed {line_number} edges.")

            logging.info(f"Prepared {len(self.documents)} documents for indexing.")
        except Exception as e:
            logging.error(f"Error processing edges: {e}")
            exit(1)


class ChromaDBIndexer:
    """Indexes documents into ChromaDB."""

    def __init__(self, collection):
        self.collection = collection

    def index_documents(self, documents, batch_size=256):
        logging.info("Indexing documents into ChromaDB.")
        for idx in range(0, len(documents), batch_size):
            batch = documents[idx : idx + batch_size]
            ids = [doc["id"] for doc in batch]
            texts = [doc["text"] for doc in batch]
            self.collection.add(ids=ids, documents=texts)
            if (idx + batch_size) % 1000 == 0 or (idx + batch_size) >= len(documents):
                logging.info(
                    f"Indexed {min(idx + batch_size, len(documents))} documents."
                )
        logging.info("Indexing completed.")


class DataPipeline:
    """Manages the entire data processing and indexing pipeline."""

    def __init__(self, nodes_file_path, edges_file_path, sampling_rate=0.002):
        self.nodes_file_path = nodes_file_path
        self.edges_file_path = edges_file_path
        self.sampling_rate = sampling_rate
        self.collection = ChromaDBInitializer.initialize_chromadb()

    def execute(self):
        node_processor = NodeProcessor(self.nodes_file_path, self.sampling_rate)
        node_processor.load_nodes()

        edge_processor = EdgeProcessor(
            self.edges_file_path,
            node_processor.nodes,
            node_processor.equivalent_curies_map,
            self.sampling_rate,
        )
        edge_processor.process_edges()

        indexer = ChromaDBIndexer(self.collection)
        indexer.index_documents(edge_processor.documents)


if __name__ == "__main__":
    Logger.setup_logging()
    load_dotenv()
    openai.api_key = config("OPENAI_API_KEY")

    pipeline = DataPipeline(
        nodes_file_path="./data/kg2c-2.8.4-nodes.jsonl",
        edges_file_path="./data/kg2c-2.8.4-edges.jsonl",
    )
    pipeline.execute()

