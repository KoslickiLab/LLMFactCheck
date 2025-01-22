import logging
import psycopg2
import json
import os
from dotenv import load_dotenv
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from decouple import config

# This file defines a class DBFactChecker that connects to a database, retrieves data, processes it using a language model, and updates the database with the results.


class DBFactChecker:
    """
    A class that handles the logic of connecting to a database, retrieving data,
    processing it using a language model, and updating the database with the results.
    """
    def __init__(self, batch_size: int = 10, env_file: str = '.env'):
        self.batch_size = batch_size
        self.env_file = env_file

        # Load environment variables
        load_dotenv(self.env_file)

        # Set up model
        self.model_name = "TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF"
        self.model_path = hf_hub_download(repo_id=self.model_name, filename="mixtral-8x7b-instruct-v0.1.Q5_K_M.gguf")
        self.model = Llama(model_path=self.model_path,
                           n_threads=64,
                           n_batch=128,
                           n_ctx=4096,
                           n_gpu_layers=96,
                           mlock=True,
                           logits_all=True)

        # Connect to DB
        
        self.conn = psycopg2.connect(
            dbname=config("DB_NAME"),
            user=config("DB_USER"),
            password=config("DB_PASSWORD"),
            host=config("DB_HOST"),
            port=config("DB_PORT"),
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("SET statement_timeout = 5000;")

        self.starting_id = self._read_starting_id()

    def _read_starting_id(self) -> int:
        """Read the starting ID from the environment file."""
        return int(os.getenv("STARTING_ID", 0))

    def _save_updated_id(self, id_value: int) -> None:
        """Save the updated starting ID to the .env file."""
        updated_lines = []
        with open(self.env_file, 'r') as file:
            lines = file.readlines()

        found = False
        for line in lines:
            if line.startswith("STARTING_ID="):
                updated_lines.append(f"STARTING_ID={id_value}\n")
                found = True
            else:
                updated_lines.append(line)

        if not found:
            updated_lines.append(f"STARTING_ID={id_value}\n")

        with open(self.env_file, 'w') as file:
            file.writelines(updated_lines)

    def _your_processing_function(self, triple: str, sentence: str):
        """
        Process a triple and a sentence with the model and return the answer and logprobs.
        This function uses a fixed prompt as defined in the original code.
        """
        prompt = f"""
        Context: 
        USER: (''Is the triple "Phase related to Follicle stimulating hormone measurement" directly or indirectly supported by the sentence: "In pre-menopause healthy females, blood was sampled weekly during one menstruation cycle and menstruation phases (follicular, ovulatory, luteal) were determined by FSH/LH levels."?',)

        ASSISTANT: Yes

        USER: (''Is the triple "Phase related to Sodium measurement" directly or indirectly supported by the sentence: "Based on a biophysical photoreceptor model, the Na(+)- and Ca(2+)-currents and concentration changes were determined from the first transient depolarization phase of the photoreceptor response."?',)

        ASSISTANT:Yes

        USER: (''Is the triple "Phase related to Bronchoalveolar Lavage" directly or indirectly supported by the sentence: "Challenge of the airways of sensitized guinea pigs with aerosolized ovalbumin resulted in an early phase of microvascular protein leakage and a delayed phase of eosinophil accumulation in the airway lumen, as measured using bronchoalveolar lavage (BAL)."?',)

        ASSISTANT: Yes

        USER: (''Does the phrase "Ciprofloxacin related to DNA Gyrase" receive at least indirect support from the statement: "Effect of ranolazine in preventing postoperative atrial fibrillation in patients undergoing coronary revascularization surgery."?',)

        ASSISTANT: No

        USER: (''Does the phrase "Ciprofloxacin related to Crohn disease" receive at least indirect support from the statement: "Recent evidence of beneficial effects of ranolazine (RAN) in type II diabetes motivates interest in the role of the late sodium current (INaL) in glucose-stimulated insulin secretion."?',)

        ASSISTANT: No

        USER: (''Does the phrase "Ciprofloxacin related to endophthalmitis" receive at least indirect support from the statement: "Furthermore, the activated Akt/mTOR signaling pathway induced by AF was further activated by ranolazine."?',)

        ASSISTANT: No


        SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. Answer 'Yes' or 'No' to directly address the query posed.                 

        USER: ('\'Does the phrase "{triple}" receive at least indirect support from the statement: "{sentence}"?',).

        ASSISTANT:

        """
        
        response = self.model(prompt=prompt, max_tokens=1, temperature=0, echo=False, logprobs=True)
        logging.info(response)
        return response["choices"][0]["text"], str(response["choices"][0]["logprobs"])

    def process_data(self):
        """Process data in batches, update the database, and track progress."""
        while True:
            self.cursor.execute("""
                SELECT "id", "triple", "sentence" 
                FROM public."tblBiomedicalFactcheck" 
                WHERE "id" >= %s
                ORDER BY "id"
                LIMIT %s
            """, (self.starting_id, self.batch_size))

            records = self.cursor.fetchall()
            logging.info(records)
            if not records:
                logging.info("No more records to process.")
                break

            for record in records:
                logging.info(record)
                id, triple, sentence = record
                logging.info(1)
                answer, logprops = self._your_processing_function(triple, sentence)
                logging.info(1)
                logprops_json = json.dumps(logprops)
                logging.info(id, answer, logprops_json)

                try:
                    self.cursor.execute("""
                        UPDATE public."tblBiomedicalFactcheck" 
                        SET "answer" = %s, "logprops" = %s
                        WHERE "id" = %s
                    """, (answer, logprops_json, id))
                except Exception as e:
                    logging.info(f"Error updating record ID {id}: {e}")
                    self.conn.rollback()

            self.conn.commit()

            logging.info(self.starting_id)
            self.starting_id += self.batch_size
            logging.info(self.starting_id)
            self._save_updated_id(self.starting_id)
            logging.info(f"Processed up to ID: {self.starting_id}")

        self.cursor.close()
        self.conn.close()
        logging.info("Data has been processed in batches and updated successfully.")


if __name__ == "__main__":
    fact_checker = DBFactChecker(batch_size=10, env_file='.env')
    fact_checker.process_data()
