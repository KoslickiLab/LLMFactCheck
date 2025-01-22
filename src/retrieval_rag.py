import logging

import networkx as nx

from load_model import ChromaDBInitializer

#Description
#The code snippet defines a class ChromaDBQuery that handles querying documents from ChromaDB.

class ChromaDBQuery:
    """Handles querying documents from ChromaDB."""

    @staticmethod
    def query_documents(question, n_results=10):
        """
        Query the initial relevant documents from ChromaDB.

        Args:
            question (str): User's query.
            n_results (int): Number of results to retrieve.

        Returns:
            list: List of top relevant documents (text).
        """
        collection = ChromaDBInitializer.initialize_chromadb()
        if collection is None:
            raise ValueError("ChromaDB collection is not initialized properly.")

        results = collection.query(query_texts=[question], n_results=n_results)

        if "documents" not in results or not results["documents"][0]:
            logging.warning("No documents found.")
            return []

        return results["documents"][0]


class RelevanceGraph:
    """Manages the relevance graph and its operations."""

    def __init__(self, initial_question, max_depth=2, n_results=10):
        self.initial_question = initial_question
        self.max_depth = max_depth
        self.n_results = n_results
        self.graph = nx.DiGraph()
        self.graph.add_node(initial_question, depth=0, text=initial_question)

    def deep_search_relevant_chunks(self):
        """
        Perform a deep search for relevant chunks and store results in a graph.

        Returns:
            nx.DiGraph: Graph representing relevant chunks and their connections.
        """
        initial_chunks = ChromaDBQuery.query_documents(
            self.initial_question, n_results=self.n_results
        )

        def expand_chunks(current_question, parent_node, current_depth):
            if current_depth > self.max_depth:
                return

            child_chunks = ChromaDBQuery.query_documents(
                current_question, n_results=self.n_results
            )

            for i, chunk in enumerate(child_chunks):
                chunk_node = f"{parent_node}_child_{i}"
                self.graph.add_node(chunk_node, depth=current_depth, text=chunk)
                self.graph.add_edge(parent_node, chunk_node)
                expand_chunks(chunk, chunk_node, current_depth + 1)

        for i, chunk in enumerate(initial_chunks):
            chunk_node = f"root_child_{i}"
            self.graph.add_node(chunk_node, depth=1, text=chunk)
            self.graph.add_edge(self.initial_question, chunk_node)
            expand_chunks(chunk, chunk_node, current_depth=2)

        return self.graph


class TreeFormatter:
    """Formats the relevance graph as a tree structure."""

    @staticmethod
    def format_relevance_tree(relevance_graph):
        """
        Format the relevance graph as a tree structure for the prompt.

        Args:
            relevance_graph (nx.DiGraph): Graph representing relevant chunks and their connections.

        Returns:
            str: Formatted string in a tree structure.
        """
        tree_formatted = []

        for node in relevance_graph.nodes:
            depth = relevance_graph.nodes[node]["depth"]
            text = relevance_graph.nodes[node]["text"]

            if depth == 0:  # Root query
                tree_formatted.append(f"Level 1: {text}\n")
                child_nodes = list(relevance_graph.successors(node))
                for i, child_node in enumerate(child_nodes, 1):
                    child_text = relevance_graph.nodes[child_node]["text"].replace(
                        "\n", "\t\n"
                    )
                    tree_formatted.append(f"\t└─ Level 2 ({i}):\n\t{child_text}\n")

                    grandchild_nodes = list(relevance_graph.successors(child_node))
                    for j, grandchild_node in enumerate(grandchild_nodes, 1):
                        grandchild_text = relevance_graph.nodes[grandchild_node][
                            "text"
                        ].replace("\n", "\t\t\n")
                        tree_formatted.append(
                            f"\t\t└─ Level 3 ({j}):\n\t\t{grandchild_text}\n"
                        )

        return "".join(tree_formatted)


class ChunkExpander:
    """Expands relevant chunks and formats the output as a tree."""

    @staticmethod
    def expand_chunks_with_tree(question):
        """
        Expand relevant chunks into a tree structure.

        Args:
            question (str): The initial question to retrieve relevant chunks.

        Returns:
            str: A formatted tree string for the prompt.
        """
        graph_manager = RelevanceGraph(question)
        relevance_graph = graph_manager.deep_search_relevant_chunks()
        return TreeFormatter.format_relevance_tree(relevance_graph)

