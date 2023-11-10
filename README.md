<div align="center">
  <img src="img/photo_2023-11-07_12-49-09.jpg" alt="Project Image">
<p>Your one-stop solution for validating predicates in various sources.</p>
</div>

## Project Description

The "LLMFactCheck" is a powerful tool designed to validate predicates in different sources, ensuring the accuracy of references and enhancing the quality of your research.


## Installation

To run the LLMFactCheck tool, you'll need to set up the necessary environment and install the required packages.

### Prerequisites

Before you begin, ensure you have Python 3.7 or later installed. You'll also need to create a virtual environment to manage dependencies.

```shell
# Create a virtual environment (venv)
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

# Install Dependencies
To install the project dependencies, use the following command:

```shell
# Copy code
pip install -r requirements.txt
```

# Usage
After completing the installation, you can run the LLMFactCheck tool using the following command:

```shell
# Copy code
# Run LLMFactCheck for Semmed database
cd src
python3 main.py --predication_file data/semmed_predicate.csv --sentence_file data/semmed_sentence.csv
```


# Project Structure
This part of the project follows a well-organized structure for easy navigation and management. 
Here's a quick overview:

**src:** Contains the main code and data for working with the Semmed database.
  
  - `main.py`: 🚀 Main file that invokes the core logic.

  - **util:**
    - `result_writing.py`: File for writing results.
    - `data_processing.py`: File for data processing.
    - `llama_interaction.py`: File for interacting with the Llama model.

  - **result:** Results of Semmed predicate validation will be stored here.
    - `semmed_result_console_app.csv`

  - **check:** Contains data you are checking and code for checking results.
    - **data:**
      - `data_file.csv`: Your data for validation.
    - `check_results.py`: File for checking results.
    
  - **previous_version:** Previous issues
    - `lcpp_llm_predicate__sentence_result.ipynb`
  

## How It Works

1. **Run the Tool**: Execute the main script from the "src" folder, and watch as the tool works its magic.

2. **View Results**: The results of the predicate validation process will be stored in the "results". You can review them to identify any issues with the references.

3. **Celebrate**: You've successfully checked predicates with LLMFactCheck! 🎉

Feel free to explore the source code in the "src" folder for customization or to understand the inner workings of the tool.

### New Features

- **Support for Multiple Sources**: LLMFactCheck now supports validating predicates in various sources, not limited to Semmed. You can easily extend its functionality for different datasets.

- **Console Application**: We've introduced a new console application that allows you to validate predicates in different sources using the command line. This provides more flexibility and ease of use, especially in environments where a database connection may not be available.
Enjoy using LLMFactCheck for all your predicate validation needs!



## Conclusion

LLMFactCheck simplifies the process of checking predicates in various sources. Whether you're a researcher or a data enthusiast, our tool will help you ensure the accuracy and quality of your data. Happy validating!

Please do not hesitate to contact us if you have any questions or see that the code needs to be improved.
