import requests
import pandas as pd
import re

api_endpoint = "https://arax.ncats.io/api/arax/v1.4/meta_knowledge_graph"


def get_query_results():
    response = requests.get(api_endpoint)

    if response.status_code == 200:
        data = response.json()

        edges = data.get('edges', [])

        triple = []
        for edge in edges:
            triple.append({
                'subject': edge.get('subject'),
                'predicate': edge.get('predicate'),
                'object': edge.get('object')
            })

        # Convert the list of triple to a pandas DataFrame
        triple_df = pd.DataFrame(triple)

        return triple_df

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


triple_df = get_query_results()

triple_list = []
for index, row in triple_df.iterrows():
    subject = process_text(row['subject'])
    predicate = process_text(row['predicate'])
    object = process_text(row['object'])
    triple = f"{subject} {predicate} {object}"
    triple_list.append(triple)

print("\n".join(triple_list))
