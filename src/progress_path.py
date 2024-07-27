import os

# Dictionary mapping task names to their progress file paths
PROGRESS_FILES = {
    'llama': os.path.join('result', 'progress', 'llama_progress.csv'),
    'llama_icl': os.path.join('result', 'progress', 'llama_icl_progress.csv'),
    'mixtral1': os.path.join('result', 'progress', 'mixtral1_progress.csv'),
    'mixtral1_icl': os.path.join('result', 'progress', 'mixtral1_icl_progress.csv'),
    'mixtral2': os.path.join('result', 'progress', 'mixtral2_progress.csv'),
    'mixtral2_icl': os.path.join('result', 'progress', 'mixtral2_icl_progress.csv'),
    'gpt_3_5_turbo': os.path.join('result', 'progress', 'gpt_3_5_turbo_progress.csv'),
    'gpt_3_5_turbo_icl': os.path.join('result', 'progress', 'gpt_3_5_turbo_icl_progress.csv'),
    'gpt_4_0': os.path.join('result', 'progress', 'gpt_4_0_progress.csv'),
    'gpt_4_0_icl': os.path.join('result', 'progress', 'gpt_4_0_icl_progress.csv')
}


# This module defines a mapping of various processing tasks to their corresponding
# progress file paths. These file paths are used to store the progress of each task.
#
# The 'os.path.join' method is used to construct the file paths, ensuring correct
# path formatting across different operating systems.
#
# Structure:
#     - Key: A string representing the name of the processing task.
#     - Value: The file path where the progress of the corresponding task is stored.
#
# Tasks and their file paths:
#     - 'llama': Path to the progress file for the 'llama' task.
#     - 'llama_icl': Path to the progress file for the 'llama_icl' task.
#     - 'gpt_3_5_turbo': Path to the progress file for the 'gpt_3_5_turbo' task.
#     - 'gpt_3_5_turbo_icl': Path to the progress file for the 'gpt_3_5_turbo_icl' task.
#     - 'gpt_4_0': Path to the progress file for the 'gpt_4_0' task.
#     - 'gpt_4_0_icl': Path to the progress file for the 'gpt_4_0_icl' task.
#
# Example:
#     To access the file path for the 'llama' task's progress:
#     >>> filepath = PROGRESS_FILES['llama']
#     >>> print(filepath)
#     'result/progress/llama_progress.csv'
