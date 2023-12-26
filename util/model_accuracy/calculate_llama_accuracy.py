import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

human_labeled_path = os.path.join(base_dir, 'model_accuracy', 'data', 'human_labeled_semmed_result.csv')
semmed_result_path = os.path.join(os.path.dirname(base_dir), 'result', 'semmed_result_console_app.csv')

human_labeled_data = pd.read_csv(human_labeled_path)
semmed_result_data = pd.read_csv(semmed_result_path)

semmed_result_data = semmed_result_data[semmed_result_data['Is Correct'] != 'Undefined']
human_labeled_data['Label'] = human_labeled_data['Label'].replace({'True': True, 'False': False})
semmed_result_data['Is Correct'] = semmed_result_data['Is Correct'].replace({'True': True, 'False': False})

# Merging dataframes on 'Predicate ID'
merged_data = pd.merge(human_labeled_data, semmed_result_data, on='Predicate ID', how='inner', validate='one_to_one')

# Extracting the relevant columns
human_labels = merged_data['Label']
semmed_results = merged_data['Is Correct']

# Calculating accuracy
accuracy = accuracy_score(human_labels, semmed_results)
incorrect = 1.0 - accuracy

print(f"Accuracy: {accuracy}")

# Creating a pie chart
plt.figure(figsize=(6,6))
plt.pie([accuracy, incorrect], labels=['Correct', 'Incorrect'], colors=['green', 'red'], autopct='%1.1f%%')

plt.title('Model Accuracy')
plt.text(0, -1.5, f"The accuracy of the model is {accuracy*100:.2f}%", ha='center', weight='bold', fontsize=12)
plt.show()
