import requests
import pandas as pd
import re

api_endpoint = "https://arax.ncats.io/api/arax/v1.4/meta_knowledge_graph"

def get_query_results():
    response = requests.get(api_endpoint)

    if response.status_code == 200:
        data = response.json()

        edges = data.get('edges', [])

        full_predicates = []
        for edge in edges:
            full_predicates.append({
                'subject': edge.get('subject'),
                'predicate': edge.get('predicate'),
                'object': edge.get('object')
            })

        # Convert the list of full predicates to a pandas DataFrame
        full_predicates_df = pd.DataFrame(full_predicates)

        return full_predicates_df

    else:
        print("Request failed")
        return None

def process_text(text):
    text = text.replace("biolink:", "")
    text = camel_case_to_words(text)
    text = text.replace("_", " ")
    return text

def camel_case_to_words(text):
    return re.sub(r'([A-Z])', r' \1', text).lower()

full_predicates_df = get_query_results()

full_predicates_list = []
for index, row in full_predicates_df.iterrows():
    subject = process_text(row['subject'])
    predicate = process_text(row['predicate'])
    object = process_text(row['object'])
    full_predicate = f"{subject} {predicate} {object}"
    full_predicates_list.append(full_predicate)

print("\n".join(full_predicates_list))

