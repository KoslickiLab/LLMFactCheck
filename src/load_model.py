from decouple import config

#Description:
#The code snippet initializes the ChromaDB collection.

class ChromaDBInitializer:
    """Initializes the ChromaDB collection."""

    @staticmethod
    def initialize_chromadb():
        from chromadb import PersistentClient
        from chromadb.utils import embedding_functions

        OPENAI_API_KEY = config("OPENAI_API_KEY")
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-ada-002",  
        )

        chroma_client = PersistentClient(path="chroma_persistent_storage")
        collection = chroma_client.get_or_create_collection(
            name="kg2c_collection", embedding_function=openai_ef
        )

        return collection
