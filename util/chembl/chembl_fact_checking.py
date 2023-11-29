import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llama_interaction import load_llama_model

chembl_api_endpoint = "https://www.ebi.ac.uk/chembl/api/data/"
model = load_llama_model()
