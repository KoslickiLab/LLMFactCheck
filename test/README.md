<p align="center"><font color="#663399" size="6"><b> Project tests </b></font></p>

This directory contains tests for the project. Tests help verify if the code functions correctly and identify any errors or issues.

## <font color="#663399"> Running Tests </font>

Make sure you are at the root of the project and then:

To run the tests, use the following command in the terminal:

```bash
pytest 
```

This command will run all the tests located within the test directory.

### Test Functionalities 🔍
The tests verify different aspects of the project's code:

`test_data_processing.py`:
- test_read_data_from_files: Checks if data is read correctly from files.
- test_process_predicate_row: Ensures correct processing of a row with a predicate.
- test_initialize_writers: Checks the proper initialization of writers.
- test_save_state: Ensures the state is saved correctly.
- test_load_state: Checks if the state is loaded correctly.
- test_process_sentence: Verifies proper sentence processing.
- test_process_data_and_fact_check: Checks proper data handling and fact checking.

`test_llama_interaction.py`:

- test_load_llama_model: This test checks if the Llama model is loaded correctly with the given parameters.
- test_get_llama_result: This test is run with different sets of prompts and expected results to check if the function correctly processes the prompts and returns the expected results. It utilizes the parametrize function from pytest to run the test with different sets of parameters.
- test_get_llama_result_exception: This test checks if the function correctly handles exceptions and returns the expected error message.

`test_progress.py`:

- test_read_progress: Checks if the progress is read correctly from the CSV file.
- test_read_progress_file_not_found: Validates the function's behavior when the progress file is not found.
- test_write_progress: Verifies that progress is correctly written to the CSV file.

`test_result_writing.py`:

- test_write_result_to_csv: Validates that the results are correctly written to the CSV file.
- test_write_progress: Ensures that progress is correctly written to the CSV file.

These tests utilize Python's built-in `unittest.mock` library to mock the file operations and `csv.writer` methods. This helps isolate the functions from the actual file system and ensure that the tests are repeatable and reliable. By patching the built-in `open` and `csv.writer` methods with `unittest.mock.patch`, we are able to simulate different scenarios and test how our functions react to them.
Each test utilizes fixtures and mocks to simulate real data and code behavior. This helps ensure that the tests are reliable and repeatable.