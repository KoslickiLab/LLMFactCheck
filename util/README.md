<p align="center"><font color="#663399" size="6"><b> Сalculating the model's accuracy & testing model </b></font></p>

This README.md file provides instructions on how to run the files for testing model and calculating the model's accuracy.

### Contents of the util directory
The util directory contains the following subdirectories and files:

#### <font color="#663399"> - model_accuracy directory</font>
This directory is used to calculate the model's accuracy. It uses human-annotated SemMedDB data to verify the model's predicate accuracy.

To see the model's accuracy, follow these steps:

Make sure you are at the root of the project and then:
```bash
cd util
cd model_accuracy
python calculate_llama_accuracy.py
```

<font color="#663399">You will see a visual representation of the model's accuracy in the form of a pie chart</font>

#### - chembl directory
This directory contains files for testing the model's performance on the ChEMBL database. It includes the chembl_predicates.py file, which generates full predicates.

To see the generated predicates, follow these steps:

Make sure you are at the root of the project and then:
```bash
cd util
cd chembl
python chembl_predicates.py
```
_Additional functionality for testing the model's performance on this database will be added in the future._