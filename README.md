
<div align="center">
  <img src="./img/project_logo.jpg" alt="Project Image">
<p>

[//]: # ([![GitHub Workflow Status]&#40;https://img.shields.io/github/actions/workflow/status/KoslickiLab/LLMFactCheck/runTest.yml&#41;]&#40;https://github.com/KoslickiLab/LLMFactCheck/actions&#41;)

[//]: # ([![codecov]&#40;https://codecov.io/gh/KoslickiLab/LLMFactCheck/graph/badge.svg?token=AZD6LBFR5P&#41;]&#40;https://codecov.io/gh/KoslickiLab/LLMFactCheck&#41;)

[//]: # ([![Quality Gate Status]&#40;https://sonarcloud.io/api/project_badges/measure?project=KoslickiLab_LLMFactCheck&metric=alert_status&#41;]&#40;https://sonarcloud.io/summary/new_code?id=KoslickiLab_LLMFactCheck&#41;)

[//]: # ([![CodeQL]&#40;https://github.com/MichaelCurrin/badge-generator/workflows/CodeQL/badge.svg&#41;]&#40;https://github.com/KoslickiLab/LLMFactCheck/actions?query=workflow%3ACodeQL "Code quality workflow status"&#41;)

[//]: # ([![License: MIT]&#40;https://img.shields.io/badge/License-MIT-green.svg&#41;]&#40;https://github.com/KoslickiLab/LLMFactCheck/blob/main/LICENSE.txt&#41;)

<!---->

[![LLama-CPP Version](https://img.shields.io/badge/LLama--CPP-0.1.78-E6E6FA)](https://github.com/llama-ai/llama-cpp)
[![Hugging Face Hub](https://img.shields.io/badge/Hugging%20Face%20Hub-0.0.12-E6E6FA)](https://huggingface.co/)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=KoslickiLab_LLMFactCheck&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=KoslickiLab_LLMFactCheck)


</p>

<div style="background-color:#E6E6FA; padding: 2px; text-align: center;">
  <h5 style="color: black; font-size: 16px;">YOUR ONE-STOP SOLUTION FOR <strong>VALIDATING PREDICATES</strong> IN VARIOUS SOURCES.</h5>
</div>
</div>

## Project Description

The "LLMFactCheck" is a powerful tool designed to validate triples in different sources, ensuring the accuracy of references and enhancing the quality of your research.

## Prerequisites

Before you begin, make sure you have the following installed: - [Miniconda](https://docs.conda.io/en/latest/miniconda.html)


### Essential for MacOS Users 🍏
To ensure a seamless experience, it's crucial to have GCC installed on your MacOS.  See [here](https://discussions.apple.com/thread/8336714).


## Installation

### Conda Environment

To run the LLMFactCheck tool, follow these steps to set up the necessary Conda environment. Follow these steps: 🛠️

1. Make sure you have completed the Prerequisites. 

2. Clone the repository:

   ```bash
   git clone https://github.com/KoslickiLab/LLMFactCheck.git
   cd LLMFactCheck
   
3. Setup the environment for LLMFactCheck by running the setup script:

   ```bash
   bash setup.sh
   
4. Activate the Conda environment:

   ```bash
    conda activate myLLMFactCheck
   
5. Create a config folder in the root of the project, create the file openai_api_key.py with the following contents:
OPENAI_API_KEY = 'your-openai-api-key'

# Usage (Run LLMFactCheck) 💡 
After completing the installation, you can run the LLMFactCheck tool using the following command:
<!---->
For LLAMA2 model:
<!---->
   ```bash
   python main.py --model llama --triple_file semmed_triple_data.csv --sentence_file semmed_sentence_data.csv
   ```
<!---->
For LLAMA model with ic:
<!---->
   ```bash
   python main.py --model llama --icl --triple_file semmed_triple_data.csv --sentence_file semmed_sentence_data.csv
   ```
<!---->
For GPT-3.5-turbo model:
<!---->
   ```bash
   python main.py --model gpt_3_5_turbo --triple_file semmed_triple_data.csv --sentence_file semmed_sentence_data.csv
   ```
<!---->
For GPT-3.5-turbo model with icl: 
<!---->
   ```bash
   python main.py --model gpt_3_5_turbo --icl --triple_file semmed_triple_data.csv --sentence_file semmed_sentence_data.csv
   ```
<!---->
For GPT-4_0 model:
<!---->
   ```bash
   python main.py --model gpt_4_0 --triple_file semmed_triple_data.csv --sentence_file semmed_sentence_data.csv
For GPT-4_0 model with icl: 
<!---->
   ```bash
   python main.py --model gpt_4_0 --icl --triple_file semmed_triple_data.csv --sentence_file semmed_sentence_data.csv
   ```
<!---->
## Project Structure
This part of the project follows a well-organized structure for easy navigation and management. 
Here's a quick overview:
<!---->
- **main.py:** Main file that invokes the core logic of all models.
<!---->
- **data:** Your data for validation.
  - `human_labeled_semmed.csv` - human-marked triples with sentences for correctness
  - `semmed_triple_data.csv` - all the columns you need for a triple from SemMedDB
  - `semmed_sentence_data.csv` - sentences from SemMedDB
  - `filtered_triple_data.csv` - only those triples from SemMedDB that match the predicates from the yaml file
  - `predicate-remap.yml` -  all predicates have been re-mapped (including mapping SemMedDB predicates to Biolink)
  - `test_df_3_5_turbo_icl` - test part human_data_semmed to determine the accuracy of the model GPT 3.5-turbo (with in-context learning)
  - `test_df_4_0_icl` - test part human_data_semmed to determine the accuracy of the model GPT 4.0 (with in-context learning)
  - `test_df_llama_icl` - test part human_data_semmed to determine the accuracy of the LLAMA2 model (with in-context learning)
<!---->
- **result:** Results of Semmed predicate validation will be stored here.
  - **progress:** - Progress of a models
  - `llama_semmed_result.csv`: results of the LLAMA2 model
  - `llama_icl_semmed_result.csv`: results of the LLAMA2 model (with in-context learning)
  - `gpt_3_5_turbo_semmed_result.csv`: results of the GPT-3.5-turbo model 
  - `gpt_3_5_turbo_icl_semmed_result.csv`: results of the GPT-3.5-turbo model (with in-context learning)
  - `gpt_4_0_semmed_result.csv`: results of GPT-4.0 model 
  - `gpt_4_0_icl_semmed_result.csv`: results of GPT-4.0 model 
<!---->
- **src:** Contains the main code for working with model and the Semmed database .
  - `data_processing.py`: File for data processing.
  - `triple_processing.py`: File for triple processing.
  - `load_model.py`: This file contains functions related to loading and initializing the language model you're using in your project. It might include setting up the Llama model or OpenAI models with appropriate configurations and API keys.
  - `get_result.py`: In this file, you can find functions related to obtaining results from the language model. This includes sending prompts to the model, receiving responses, and processing the model's output to extract meaningful information or answers.
  - `result_writing.py`: File for writing results.
  - `progress.py` - File to track the progress of predicate validation.
  - `progress_path.py`: This file related to managing file paths for storing progress information.
  - `progressing.py`: The purpose of this file is to manage the progression of tasks and processes within the project. 

<!---->
- **util:** The util directory contains the following subdirectories and files:
    <!---->
    - <font color="#663399"> model_accuracy directory</font>
      
      This directory is used to calculate the model's accuracy. It uses human-annotated SemMedDB data to verify the model's ptriple accuracy.
             
      To see the model's accuracy, follow these steps:
      Make sure you are at the root of the project and then:
      <!---->
      For LLAMA2 model:
      <!---->
      ```bash
      cd util
      cd model_accuracy
      python accuracy.py --model llama --test_df_file test_df --result_file semmed_result
      ```
      <!---->
      For LLAMA2 model with ICL:
      <!---->
      ```bash
      cd util
      cd model_accuracy
      python accuracy.py --model llama --icl --test_df_file test_df --result_file semmed_result
      ```
      <!---->
      For GPT-3.5.-turbo model:
      <!---->
      ```bash
      cd util
      cd model_accuracy
      python accuracy.py --model gpt_3_5_turbo --test_df_file test_df --result_file semmed_result
      ```
      <!---->
      For GPT-3.5.-turbo model with ICL:
      <!---->
      ```bash
      cd util
      cd model_accuracy
      python accuracy.py --model gpt_3_5_turbo --icl --test_df_file test_df --result_file semmed_result
      ```
      <!---->
      For GPT-4.0 model:
      <!---->
      ```bash
      cd util
      cd model_accuracy
      python accuracy.py --model gpt_4_0 --test_df_file test_df --result_file semmed_result
      ```
      <!---->
      For GPT-4.0 model with ICL:
      <!---->
      ```bash
      cd util
      cd model_accuracy
      python accuracy.py --model gpt_4_0 --icl --test_df_file test_df --result_file semmed_result
      ```
      <!---->
      <font color="#663399">You will see a visual representation of the model's accuracy in the form of a pie chart</font>
      <!---->

    <!---->
    - chembl directory
           
      This directory contains files for testing the model's performance on the ChEMBL database. 
      It includes the `chembl_triple.py` file, which generates triples.
      If You want to try it:
      Make sure you are at the root of the project and then:
      ```bash
      cd util
      cd chembl
      python chembl_triple.py
      ```
      Then, this directory includes  the `semmed_triple_mapping.py` file, which processes the data from the semmed_triple_data.csv file, creates a new 'TRIPLE' column from this data, and then filters this data to select only those triples that match the predicates specified in the predicate-remap.yaml file. As a result, only those triples from SemMedDB that match the predicates from the yaml file are displayed, and are also written to the filtered_triple_data.csv file in the project data folder.
      If You want to try it:
      Make sure you are at the root of the project and then:
      ```bash
      cd util
      cd chembl
      python semmed_triple_mapping.py
      ```
      You don't have to do this (unless you think it's necessary), because we've already done this work and the result is already in the filtered_triple_data.py file
      <!---->
<!---->
- **test:** This directory contains tests for the project. Tests help verify if the code functions correctly and identify any errors or issues.

    Running Tests:
    Make sure you are at the root of the project and then:

    To run the tests, use the following command in the terminal:
     ```bash
     pytest 
     ```
     This command will run all the tests located within the test directory.
     <!---->

  These tests utilize Python's built-in unittest.mock library to mock the file operations and csv.writer methods. This helps isolate the functions from the actual file system and ensure that the tests are repeatable and reliable. By patching the built-in open and csv.writer methods with unittest.mock.patch, we are able to simulate different scenarios and test how our functions react to them. Each test utilizes fixtures and mocks to simulate real data and code behavior. This helps ensure that the tests are reliable and repeatable.

## How It Works

1. **Run the Tool**: Execute the main script, and watch as the tool works its magic.

2. **View Results**: The results of the triple validation process will be stored in the "result". You can review them to identify any issues with the references.

3. **Celebrate**: You've successfully checked triples with LLMFactCheck! 🎉

Feel free to explore the source code in the "src" folder for customization or to understand the inner workings of the tool.

### New Features

- **Support for Multiple Sources**: LLMFactCheck now supports validating triples in various sources, not limited to Semmed. You can easily extend its functionality for different datasets.

- **Console Application**: We've introduced a new console application that allows you to validate triples in different sources using the command line. This provides more flexibility and ease of use, especially in environments where a database connection may not be available.
Enjoy using LLMFactCheck for all your triple validation needs!



## Conclusion

LLMFactCheck simplifies the process of checking triples in various sources. Whether you're a researcher or a data enthusiast, our tool will help you ensure the accuracy and quality of your data. Happy validating!

Please do not hesitate to contact us if you have any questions or see that the code needs to be improved.
