import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

IS_CORRECT_COLUMN = 'Is Correct'
PREDICATE_ID_COLUMN = 'Predicate ID'


def calculate_accuracy(test_df_path, result_path):
    # Load test data
    test_df = pd.read_csv(test_df_path)
    result_data = pd.read_csv(result_path)

    print(f"Rows in test_df: {len(test_df)}")
    print(f"Rows in result_data: {len(result_data)}")

    # Data preprocessing
    test_df['Label'] = test_df['Label'].replace({'True': True, 'False': False, 'Undefined': np.nan})
    result_data[IS_CORRECT_COLUMN] = (
        result_data[IS_CORRECT_COLUMN].replace({'True': True, 'False': False, 'Undefined': np.nan}))

    # Merging dataframes
    merged_data = pd.merge(test_df, result_data, on=PREDICATE_ID_COLUMN, how='inner', validate='one_to_one')

    print(f"Rows in merged_data: {len(merged_data)}")

    test_ids = set(test_df[PREDICATE_ID_COLUMN])
    result_ids = set(result_data[PREDICATE_ID_COLUMN])
    unmatched_result_count = len(result_ids - test_ids)

    print(f"Unmatched {PREDICATE_ID_COLUMN} in result_data: {unmatched_result_count}")
    if unmatched_result_count > 0:
        print("Unmatched Predicate IDs may be due to missing entries in either test or result datasets and it's ok ;) ")

    # Extracting relevant columns
    test_labels = merged_data['Label']
    results = merged_data[IS_CORRECT_COLUMN]

    # Calculating accuracy and statistics
    correct_predictions = np.sum(results == test_labels)
    incorrect_predictions = np.sum(results != test_labels)
    true_results = np.sum(results is True)
    false_results = np.sum(results is False)
    undefined_results = np.sum(pd.isna(results))

    accuracy = correct_predictions / (correct_predictions + incorrect_predictions)

    stats = {
        'total_results': len(merged_data),
        'correct': correct_predictions,
        'incorrect': incorrect_predictions,
        'true_results': true_results,
        'false_results': false_results,
        'undefined_results': undefined_results
    }

    return accuracy, stats


def plot_accuracy(accuracy, stats, title):
    incorrect = 1.0 - accuracy

    # Customizing the style
    plt.style.use('ggplot')

    font = {'family': 'serif', 'color':  'darkgrey', 'weight': 'normal', 'size': 16}

    # Creating a pie chart
    _, ax = plt.subplots(figsize=(12, 12))
    ax.pie([accuracy, incorrect], labels=['Correct', 'Incorrect'],
           colors=['#4CAF50', 'lightgrey'], autopct='%1.1f%%', startangle=140)
    ax.set_title(title, fontdict=font)

    # Displaying model accuracy and additional statistics
    plt.figtext(0.5, 0.95, f"**{title} Model Accuracy: {accuracy:.2f}**",
                ha='center', fontsize=14, weight='bold', color='purple')

    # Adjusted positions of the text, with styling
    plt.figtext(0.25, 0.08, f"Total results: {stats['total_results']}", ha='left')
    plt.figtext(0.25, 0.05, f"Correct predictions: {stats['correct']}", ha='left')
    plt.figtext(0.25, 0.02, f"Incorrect predictions: {stats['incorrect']}", ha='left')
    plt.figtext(0.65, 0.08, f"True results: {stats['true_results']}", ha='left')
    plt.figtext(0.65, 0.05, f"False results: {stats['false_results']}", ha='left')
    plt.figtext(0.65, 0.02, f"Undefined results: {stats['undefined_results']}", ha='left')

    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Calculate and plot model accuracy.')
    parser.add_argument('--model', required=True, help='Name of the model')
    parser.add_argument('--icl', action='store_true', help='Flag to indicate in-context learning')
    parser.add_argument('--test_df_file', required=True, help='Name of the test dataframe file')
    parser.add_argument('--result_file', required=True, help='Name of the result file')

    args = parser.parse_args()

    # Define the path to the data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data')
    result_dir = os.path.join(base_dir, 'result')

    # Construct the file paths
    if args.icl:
        # For models with ICL, use the specified test dataframe file
        test_df_file = os.path.join(data_dir, f"{args.test_df_file}_{args.model}_icl.csv")
    else:
        # For models without ICL, use the human_labeled_semmed.csv file
        test_df_file = os.path.join(data_dir, 'human_labeled_semmed.csv')
        # Uncomment the line below this annotation (and comment, pls, line on top)
        # to use the specified test dataframe file for standart model too.
        # test_df_file = os.path.join(data_dir, f"{args.test_df_file}_{args.model}_icl.csv")

    result_file = os.path.join(result_dir, f"{args.model}{'_icl' if args.icl else ''}_{args.result_file}.csv")

    accuracy, total_results = calculate_accuracy(test_df_file, result_file)
    print(f"**{args.model} Model Accuracy: {accuracy:.2f}**")
    print(f"Total test results: {total_results}")

    model_title = f'{args.model} {"(with ICL)" if args.icl else ""}'
    plot_accuracy(accuracy, total_results, f'{model_title} Model Accuracy')


if __name__ == "__main__":
    main()
