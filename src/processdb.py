import json
import ast
import psycopg2
from psycopg2.extras import execute_batch
from decouple import config
from logger_config import Logger
import logging

class DatabaseConnection:
    """Manages the database connection and cursor."""

    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=config("DB_NAME"),
            user=config("DB_USER"),
            password=config("DB_PASSWORD"),
            host=config("DB_HOST"),
            port=config("DB_PORT"),
        )
        self.cursor = self.conn.cursor()

    def execute_batch_insert(self, data_batch, query):
        """Executes batch insert into the database."""
        execute_batch(self.cursor, query, data_batch)
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        self.cursor.close()
        self.conn.close()

class NodeLoader:
    """Loads nodes and equivalent CURIEs from the nodes file."""

    def __init__(self, nodes_file_path):
        self.nodes_file_path = nodes_file_path
        self.nodes = {}
        self.equivalent_curies_map = {}

    def load_nodes(self):
        """Loads all nodes into memory."""
        with open(self.nodes_file_path, "r") as nodes_file:
            for line in nodes_file:
                node_data = json.loads(line)
                name = node_data.get("name") or (
                    node_data.get("all_names")[0]
                    if "all_names" in node_data and node_data["all_names"]
                    else "Unknown"
                )
                self.nodes[node_data["id"]] = name
                for curie in node_data.get("equivalent_curies", []):
                    self.equivalent_curies_map[curie] = name

class EdgeProcessor:
    """Processes edges and prepares data for database insertion."""

    def __init__(self, edges_file_path, nodes, equivalent_curies_map, batch_size=10000):
        self.edges_file_path = edges_file_path
        self.nodes = nodes
        self.equivalent_curies_map = equivalent_curies_map
        self.batch_size = batch_size
        self.insert_data = []

    def process_edges(self):
        """Processes edges and prepares them for database insertion."""
        with open(self.edges_file_path, "r") as edges_file:
            for line in edges_file:
                edge = json.loads(line)

                if edge.get("primary_knowledge_source") == "infores:semmeddb":
                    publications_info_raw = edge.get("publications_info", "{}")
                    publications_info = self._parse_publications_info(publications_info_raw)

                    sentence = next(
                        (info.get("sentence", "") for info in publications_info.values()), ""
                    )
                    subject_name = self._get_node_name(edge["subject"])
                    object_name = self._get_node_name(edge["object"])
                    predicate_name = self._get_node_name(edge["predicate"])
                    fact = f"{subject_name} {predicate_name} {object_name}"

                    self.insert_data.append((edge["id"], fact, sentence))

                    if len(self.insert_data) >= self.batch_size:
                        yield self.insert_data
                        self.insert_data.clear()

        # Yield any remaining data
        if self.insert_data:
            yield self.insert_data

def main():
    # Initialize components
    Logger.setup_logging()
    db = DatabaseConnection()
    node_loader = NodeLoader("kg2c-2.8.4-nodes.jsonl")
    node_loader.load_nodes()

    edge_processor = EdgeProcessor(
        edges_file_path="kg2c-2.8.4-edges.jsonl",
        nodes=node_loader.nodes,
        equivalent_curies_map=node_loader.equivalent_curies_map,
    )

    # Database insertion query
    query = """
        INSERT INTO public."tblkg2c-2-8-4Dataset" ("nodeDataID", "triple", "sentence")
        VALUES (%s, %s, %s)
    """

    # Process edges and insert data into the database
    try:
        for data_batch in edge_processor.process_edges():
            db.execute_batch_insert(data_batch, query)
        logging.info("Data has been inserted into the database successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
