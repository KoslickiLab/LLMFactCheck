#! /bin/bash
set -euo pipefail
# Setup environment for running LLMFactCheck

# Check if the LLMFactCheck environment exists
ENV_NAME="myLLMFactCheck"
tests=$(conda env list | awk '{print $1}' | grep -w $ENV_NAME | wc -l)

if [ $check -eq 1 ]; then
    echo "The environment '$ENV_NAME' already exists. Please activate it by running 'conda activate $ENV_NAME'."
else
    # Create a new environment using the provided YAML file
    conda env create -n $ENV_NAME -f env/LLMFactCheck.yml

    if [ $? -eq 0 ]; then
        echo "The environment '$ENV_NAME' has been successfully created."
        echo "Activate it by running 'conda activate $ENV_NAME'."

        # Check if there's a pip section in the YAML file
        PIP_SECTION=$(grep "pip:" env/LLMFactCheck.yml | wc -l)

        # Install pip packages if 'pip:' section is found
        if [ $PIP_SECTION -gt 0 ]; then
            echo "Installing pip packages listed in LLMFactCheck.yml"
            pip install -r <(grep "pip:" -A 1 env/LLMFactCheck.yml | tail -n 1 | awk '{print $2}')
        fi
    else
        echo "There was a problem creating the environment '$ENV_NAME'. Please check the error messages above."
    fi
fi
