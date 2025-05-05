import json
import logging
import random
import re
from datetime import datetime

from decouple import config
from dotenv import load_dotenv
from openai import OpenAI

from langfuse_config import langfuse
from retrieval_rag import ChunkExpander
from logger_config import Logger

#Description:
#The code snippet defines a class DatasetManager that handles dataset operations.

class DatasetManager:
    """Handles dataset operations."""

    def __init__(self):
        from langfuse_config import langfuse
        self.langfuse = langfuse

    def load_local_dataset(self, file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            random.shuffle(data)
            logging.info(f"Dataset loaded and shuffled from {file_path}.")
            return data
        except Exception as e:
            logging.error(f"Error loading dataset from {file_path}: {e}")
            raise e

    def get_dataset(self, dataset_name):
        try:
            return self.langfuse.get_dataset(dataset_name)
        except Exception as e:
            logging.error(f"Error retrieving dataset {dataset_name}: {e}")
            return None

    def create_dataset(self, dataset_name):
        try:
            self.langfuse.create_dataset(name=dataset_name)
            logging.info(f"Dataset {dataset_name} created successfully.")
        except Exception as e:
            logging.error(f"Error creating dataset {dataset_name}: {e}")
            raise e

    def upload_items_to_langfuse(self, dataset_name, items):
        for item in items:
            try:
                self.langfuse.create_dataset_item(
                    dataset_name=dataset_name,
                    input={
                        "triple": item["input"]["triple"],
                        "sentence": item["input"]["sentence"],
                    },
                    expected_output=item["validation_result"],
                )
                langfuse.trace(
                    name="Dataset item uploaded",
                    input=item["input"],
                    expected_output=item["validation_result"],
                )
            except Exception as e:
                logging.error(f"Failed to upload item: {item} - {e}")
        logging.info(f"All items uploaded to dataset {dataset_name}.")


class RAGProcessor:
    """Handles processing of triples using Retrieval-Augmented Generation (RAG)."""

    def __init__(self, openai_client, model):
        self.client = openai_client
        self.model = model

    def extract_answer(self, llm_response):
        """
        Extract the 'Answer' from LLM response.
        Args:
            llm_response (str): Full response from LLM.
        Returns:
            str: The extracted answer, or 'No Answer Found' if not present.
        """
        if not isinstance(llm_response, str):
            logging.error("Invalid input to extract_answer: not a string.")
            return "No Answer Found"

        match = re.search(r"Answer:\s*(Yes|No)", llm_response, re.IGNORECASE)
        return match.group(1) if match else "No Answer Found"

    def process_triple(self, triple, sentence):
        question = f'Does the phrase "{triple}" receive at least indirect support from the statement: "{sentence}"?'
        relevant_chunks = ChunkExpander.expand_chunks_with_tree(question)

        if not relevant_chunks:
            logging.warning(f"No relevant documents found for triple: {triple}")
            return "No Answer Found", "", ""

        prompt = self.create_prompt(triple, sentence, relevant_chunks)
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}]
            )
            response_content = response.choices[0].message.content
            final_answer = self.extract_answer(response_content)
        except Exception as e:
            logging.error(f"Error during OpenAI API call: {e}")
            return "No Answer Found", prompt, ""

        return final_answer, prompt, response_content

    @staticmethod
    def create_prompt(triple, sentence, relevant_chunks):
        prompt = f"""
    You are a computational biologist specializing in the evaluation of scientific claims. Your role is to apply critical thinking and domain-specific expertise to assess the validity of scientific statements based on provided evidence and data.
    
	Follow the instructions below to provide your answer.
   ** instructions **
   Follow a structured, step-by-step approach:
    1. Analyze the provided triple and the associated statement step-by-step.
    2. Explain your reasoning process, detailing how (or if) the statement supports the triple.
    3. Determine if the triple receives at least indirect support from the statement.
        - Answer "Yes" if the statement provides clear and sufficient support (direct or indirect).
        - Answer "No" if the support is ambiguous, unclear, or absent.
    4. Provide your final conclusion in the exact format:
        Answer: Yes
    or
        Answer: No

    Failure to provide this explicit answer will result in the response being marked as incomplete.
	
	---
    ** USER: **
    ```
    'Does the phrase "{triple}" receive at least indirect support from the statement: "{sentence}"?'
    ```
	** ASSISTANT response: **
    ```
    <Your step-by-step reasoning and final answer>
    Answer: Yes or No
    ```
	---

	
    Use the context below to evaluate the statement. The information is structured in hierarchical levels of relevance, from Level 1 (most relevant) to Level 3 (subordinate relationships). Your analysis should prioritize higher-level data when making decisions.
	Based on your analysis and the context below, provide a conclusion:
    ========= Relevant triples with subordinate clauses | BEGIN =========
    {relevant_chunks}
    ========= Relevant triples with subordinate clauses | END =========


    ---
    **Examples:**
    ---

    
    **USER:**
    ```
    'Is the triple "Phase related to Follicle stimulating hormone measurement" directly or indirectly supported by the sentence: "In pre-menopause healthy females, blood was sampled weekly during one menstruation cycle and menstruation phases (follicular, ovulatory, luteal) were determined by FSH/LH levels."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

		1. The triple states: "Phase related to Follicle stimulating hormone measurement."
		- This implies that a particular phase (in some physiological or biological context) is determined or associated with the measurement of Follicle Stimulating Hormone (FSH).

		2. The sentence given is: "In pre-menopause healthy females, blood was sampled weekly during one menstruation cycle and menstruation phases (follicular, ovulatory, luteal) were determined by FSH/LH levels."

		3. Breakdown of the sentence:
		- The context is about menstrual cycles in pre-menopausal healthy females.
		- Blood samples were taken weekly during a full menstruation cycle.
		- The specific menstruation phases—follicular, ovulatory, and luteal—were identified (determined) by measuring the levels of hormones, specifically FSH and LH.

		4. The phrase "were determined by FSH/LH levels" clearly indicates that the definition or identification of the menstrual phases relied, at least in part, on the measurement of Follicle Stimulating Hormone. In other words, the hormone levels are used as an indicator or criterion to decide which phase the menstrual cycle is currently in.

		5. Therefore, the statement shows that the "Phase" (referring to the menstruation phase) is indeed related to the measurement of FSH, among other hormones (LH). The triple is effectively supported: the link between "Phase" and "Follicle stimulating hormone measurement" is explicitly mentioned.

		**Conclusion:**
		The sentence provides direct support that menstrual cycle phases are related to FSH measurements.

		**Final Answer:**
		Answer: Yes

    ```
    ---
    **USER:**
    ```
    'Is the triple "Phase related to Sodium measurement" directly or indirectly supported by the sentence: "Based on a biophysical photoreceptor model, the Na(+)- and Ca(2+)-currents and concentration changes were determined from the first transient depolarization phase of the photoreceptor response."?'
    ```
    
    **ASSISTANT:**
    ```

	**Step-by-step reasoning:**

1. Examine the triple: "Phase related to Sodium measurement."  
   - This triple suggests that there is a particular phase in a process that is relevant to or connected with measuring sodium (Na+) levels or currents.

2. Examine the sentence:   
   "Based on a biophysical photoreceptor model, the Na(+)- and Ca(2+)-currents and concentration changes were determined from the first transient depolarization phase of the photoreceptor response."

3. Breakdown of the sentence:  
   - The sentence describes a scenario where measurements of Na(+) and Ca(2+) currents (as well as their concentration changes) are being taken.  
   - These measurements are derived specifically from the "first transient depolarization phase" of the photoreceptor response.

4. Linking the triple and the sentence:  
   - The triple indicates a relationship between some "phase" and the measurement of sodium (Na+).  
   - The sentence states that Na(+) currents and concentration changes were determined from a specific phase ("the first transient depolarization phase") in a photoreceptor model.

5. Does the sentence support the triple?  
   - Yes. The sentence clearly shows that there is a phase during which Na(+) measurements (currents and concentration changes) are taken or determined.  
   - This directly connects the concept of a "phase" to the measurement of sodium, thus supporting the triple.

**Conclusion:**  
The sentence provides at least indirect (and arguably direct) support that sodium measurement is related to a specific phase.

**Final Answer:**  
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Is the triple "Phase related to Bronchoalveolar Lavage" directly or indirectly supported by the sentence: "Challenge of the airways of sensitized guinea pigs with aerosolized ovalbumin resulted in an early phase of microvascular protein leakage and a delayed phase of eosinophil accumulation in the airway lumen, as measured using bronchoalveolar lavage (BAL)."?'
    ```
    
    **ASSISTANT:**
    ```
**Step-by-step reasoning:**

1. Triple under consideration: "Phase related to Bronchoalveolar Lavage"
   - This means we are looking for whether a "phase" is associated or determined using bronchoalveolar lavage (BAL).

2. Given sentence:
   "Challenge of the airways of sensitized guinea pigs with aerosolized ovalbumin resulted in an early phase of microvascular protein leakage and a delayed phase of eosinophil accumulation in the airway lumen, as measured using bronchoalveolar lavage (BAL)."

3. Breakdown of the sentence:
   - The experiment involves sensitized guinea pigs challenged with aerosolized ovalbumin.
   - Two phases are observed in the response:
     - An early phase characterized by microvascular protein leakage.
     - A delayed phase characterized by eosinophil accumulation.
   - Crucially, these phases were measured using bronchoalveolar lavage (BAL).

4. Link to the triple:
   - The triple states that there is a "phase" related to BAL.
   - The sentence explicitly says that the different phases (early and delayed) are measured by bronchoalveolar lavage.
   - Thus, it shows a direct relationship between the phases of the response and the use of bronchoalveolar lavage as a measurement technique.

5. Conclusion:
   - The sentence confirms that BAL is used to identify or quantify the phases observed in the guinea pigs' airway response.
   - Therefore, it supports the triple that indicates a relationship between a phase and bronchoalveolar lavage.

**Final Answer:**
Answer: Yes

    ```
    ---
    **USER:**
    ```
    'Does the phrase "Ciprofloxacin related to DNA Gyrase" receive at least indirect support from the statement: "Effect of ranolazine in preventing postoperative atrial fibrillation in patients undergoing coronary revascularization surgery."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple in question: "Ciprofloxacin related to DNA Gyrase"

   - This triple suggests a relationship between the antibiotic ciprofloxacin and DNA gyrase (which is a bacterial enzyme targeted by ciprofloxacin).

2. The provided statement:  
   "Effect of ranolazine in preventing postoperative atrial fibrillation in patients undergoing coronary revascularization surgery."

3. Breakdown of the statement:  
   - The statement focuses on the effect of the drug ranolazine in preventing a specific cardiac complication (postoperative atrial fibrillation) in patients who have undergone coronary revascularization surgery.
   - It does not mention ciprofloxacin or any antibiotic.
   - It does not mention DNA gyrase, which is typically associated with bacterial function and not directly related to the cardiac context described.
   - No indirect references that might connect ranolazine or the procedure to ciprofloxacin or DNA gyrase are apparent.

4. Does the statement support the triple?
   - The triple is about ciprofloxacin and DNA gyrase, a known antibiotic-enzyme relationship.
   - The statement is about ranolazine and atrial fibrillation in a cardiac surgery context, with no known link to ciprofloxacin, antibiotics, or DNA gyrase.
   - Therefore, there is no support (direct or indirect) for the "Ciprofloxacin related to DNA Gyrase" triple from this statement.

**Final Answer:**
Answer: No
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Ciprofloxacin related to Crohn disease" receive at least indirect support from the statement: "Recent evidence of beneficial effects of ranolazine (RAN) in type II diabetes motivates interest in the role of the late sodium current (INaL) in glucose-stimulated insulin secretion."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple under evaluation: "Ciprofloxacin related to Crohn disease"
   - This suggests a relationship between the antibiotic ciprofloxacin and the condition Crohn disease.

2. The provided statement:  
   "Recent evidence of beneficial effects of ranolazine (RAN) in type II diabetes motivates interest in the role of the late sodium current (INaL) in glucose-stimulated insulin secretion."

3. Breakdown of the given statement:
   - The statement focuses on ranolazine and its beneficial effects in type II diabetes.
   - It mentions interest in the late sodium current (INaL) and its role in insulin secretion.
   - There is no mention of ciprofloxacin, no mention of any antibiotic, and no mention of Crohn disease or any inflammatory bowel condition.

4. Does this statement support the triple?
   - The triple requires some link between ciprofloxacin and Crohn disease.
   - The statement is entirely about a cardiovascular/metabolic drug (ranolazine) in the context of type II diabetes, not about antibiotics, not about gastrointestinal diseases like Crohn.
   - There is no direct or indirect support for linking ciprofloxacin to Crohn disease here.

**Final Answer:**
Answer: No
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Ciprofloxacin related to endophthalmitis" receive at least indirect support from the statement: "Furthermore, the activated Akt/mTOR signaling pathway induced by AF was further activated by ranolazine."?'
    ```
    
    **ASSISTANT:**
    ```
   **Step-by-step reasoning:**

1. The triple under consideration: "Ciprofloxacin related to endophthalmitis."
   - This implies a connection between the antibiotic ciprofloxacin and the eye infection endophthalmitis.

2. The provided statement:
   "Furthermore, the activated Akt/mTOR signaling pathway induced by AF was further activated by ranolazine."

3. Breakdown of the statement:
   - The sentence describes a molecular pathway (Akt/mTOR) being activated by AF, and this effect being further enhanced by the drug ranolazine.
   - There is no mention of ciprofloxacin or any antibiotic.
   - There is no mention of endophthalmitis, which is an ocular infection.

4. Linking the triple and the statement:
   - The triple is about ciprofloxacin and a specific eye condition (endophthalmitis).
   - The statement deals with molecular signaling pathways and a different drug (ranolazine). There is no apparent link to antibiotics or eye infections.

5. Conclusion:
   - Since neither ciprofloxacin nor endophthalmitis is mentioned or even indirectly implied, the statement does not provide support for the triple.

**Final Answer:**
Answer: No
    ```
    ---
    **USER:**
    ```
    'Is the triple "Gene X related to Protein Y expression" directly or indirectly supported by the sentence: "Overexpression of Gene X leads to an increase in Protein Y levels in neuronal cells."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple is: "Gene X related to Protein Y expression."
   - This means we’re looking for a connection between Gene X and the expression (or levels) of Protein Y.

2. The provided sentence is: "Overexpression of Gene X leads to an increase in Protein Y levels in neuronal cells."
   - The sentence explicitly states that when Gene X is overexpressed, there is a corresponding increase in Protein Y levels. 
   - This implies a direct relationship between the presence or activity of Gene X and the expression of Protein Y.

3. Since "overexpression" of Gene X results in increased Protein Y, the statement directly supports the notion that Gene X is related to (or influences) Protein Y expression.

**Final Answer:**  
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Vitamin D related to Bone Density" receive at least indirect support from the statement: "Participants who received Vitamin D supplements showed improved calcium absorption rates."?'
    ```
    
    **ASSISTANT:**
    ```
   **Step-by-step reasoning:**

1. The triple is: "Vitamin D related to Bone Density."

2. The statement given is: "Participants who received Vitamin D supplements showed improved calcium absorption rates."

3. Evaluating the connection:
   - The statement directly links Vitamin D supplementation to improved calcium absorption.
   - While the sentence does not explicitly mention bone density, it is well-established in medical and biological contexts that calcium absorption is a critical factor for maintaining and improving bone density.
   - Increased calcium absorption, facilitated by Vitamin D, indirectly supports the idea that Vitamin D is related to bone density because better calcium uptake usually contributes to stronger, denser bones.

4. Therefore, although the statement does not say "bone density" outright, it provides a key piece of evidence (improved calcium absorption) that is closely associated with bone density improvement. This can be seen as at least indirect support.

**Final Answer:**
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Is the triple "Enzyme A related to Metabolic Pathway B" directly or indirectly supported by the sentence: "Inhibition of Enzyme A disrupts the metabolic pathway B, leading to reduced synthesis of essential metabolites."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple states: "Enzyme A related to Metabolic Pathway B."  
   - This means we are looking to see if there is a relationship between Enzyme A and Metabolic Pathway B.

2. The sentence given is: "Inhibition of Enzyme A disrupts the metabolic pathway B, leading to reduced synthesis of essential metabolites."  
   - This sentence explicitly states that if Enzyme A is inhibited, Metabolic Pathway B is disrupted.
   - Disruption of Metabolic Pathway B upon inhibition of Enzyme A suggests a direct link or dependency of the pathway on the enzyme.

3. Since the sentence clearly connects Enzyme A activity to the proper function of Metabolic Pathway B, it provides direct support for the triple.

**Final Answer:**
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Antibiotic Z related to Heart Disease" receive at least indirect support from the statement: "Long-term use of Antibiotic Z has been associated with alterations in gut microbiota composition."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple is: "Antibiotic Z related to Heart Disease."  
   - This implies we are looking for some evidence that Antibiotic Z has a connection to heart disease.

2. The provided statement:  
   "Long-term use of Antibiotic Z has been associated with alterations in gut microbiota composition."

3. Evaluating the connection:
   - The statement links long-term use of Antibiotic Z to changes in the gut microbiome.
   - It does not mention heart disease or any cardiovascular condition.
   - While the gut microbiota can have systemic effects, the statement does not indicate any direct or indirect link to heart disease.  
   - Without additional context or established scientific knowledge stated in the given sentence, it's not possible to infer a connection between Antibiotic Z and heart disease solely from altered gut microbiota composition.

4. Conclusion:
   - The provided sentence does not support, even indirectly, that Antibiotic Z is related to heart disease.

**Final Answer:**
Answer: No
    ```
    ---
    **USER:**
    ```
    'Is the triple "Protein Z related to Cellular Apoptosis" directly or indirectly supported by the sentence: "Activation of Protein Z triggers the apoptotic pathways leading to programmed cell death."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple: "Protein Z related to Cellular Apoptosis"  
   - This states that Protein Z is related to or associated with the process of cellular apoptosis.

2. The provided sentence:  
   "Activation of Protein Z triggers the apoptotic pathways leading to programmed cell death."

3. Analysis:  
   - The sentence explicitly states that when Protein Z is activated, it initiates apoptotic pathways.
   - "Apoptotic pathways" are the mechanisms by which cells undergo apoptosis (programmed cell death).
   - Thus, the sentence clearly connects Protein Z activation to the induction of cellular apoptosis.

4. Conclusion:  
   - The sentence directly supports the relationship between Protein Z and cellular apoptosis.

**Final Answer:**  
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Hormone A related to Metabolic Syndrome" receive at least indirect support from the statement: "Studies have shown that Hormone A levels are elevated in individuals with insulin resistance."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple is: "Hormone A related to Metabolic Syndrome."
   - This suggests that Hormone A should have some connection or association with metabolic syndrome.

2. The provided statement:
   "Studies have shown that Hormone A levels are elevated in individuals with insulin resistance."

3. Consider the relationship between insulin resistance and metabolic syndrome:
   - Insulin resistance is widely recognized as a key component and risk factor of metabolic syndrome. Metabolic syndrome is typically characterized by a cluster of conditions, including insulin resistance, high blood pressure, abnormal cholesterol levels, and excess body fat around the waist.
   - Therefore, if Hormone A levels are elevated in individuals with insulin resistance, it indirectly links Hormone A to a core element of metabolic syndrome.

4. Although the statement does not explicitly mention metabolic syndrome, the presence of elevated Hormone A in people with insulin resistance strongly hints at an involvement of Hormone A in metabolic syndrome. Thus, we can say the statement provides at least indirect support for the triple.

**Final Answer:**
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Is the triple "Gene Y related to Immune Response" directly or indirectly supported by the sentence: "Knockout of Gene Y resulted in a diminished immune response to viral infections in mice."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple: "Gene Y related to Immune Response" implies there should be a connection between Gene Y and the immune response.

2. The given sentence: "Knockout of Gene Y resulted in a diminished immune response to viral infections in mice."

3. Analysis:
   - The sentence clearly states that removing Gene Y (knockout) led to a reduced immune response.
   - This indicates that Gene Y plays a role in normal immune functioning.
   - By losing Gene Y, the mice show a diminished (weakened) immune response, directly linking Gene Y to immune response mechanisms.

4. Conclusion:
   - The statement directly supports the triple by showing Gene Y’s involvement in maintaining a proper immune response.

**Final Answer:**  
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Medication B related to Kidney Function" receive at least indirect support from the statement: "Long-term use of Medication B has been linked to changes in renal biomarkers."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple: "Medication B related to Kidney Function."
   - This indicates a potential relationship between Medication B and how the kidneys work or function.

2. The given statement: 
   "Long-term use of Medication B has been linked to changes in renal biomarkers."
   
3. Analysis:
   - "Renal" refers to the kidneys.
   - Biomarkers are measurable substances in the body whose changes can indicate alterations in organ function or health status.
   - Changes in renal biomarkers generally reflect changes in kidney function or health.
   - Thus, if Medication B is linked to changes in renal biomarkers, it implies that Medication B affects kidney-related parameters.

4. Conclusion:
   - Since renal biomarkers are directly associated with kidney function, the statement indirectly supports that Medication B is related to kidney function.

**Final Answer:**
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Is the triple "Receptor C related to Neurotransmitter D release" directly or indirectly supported by the sentence: "Binding of ligand E to Receptor C modulates the release of Neurotransmitter D in synaptic clefts."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple is: "Receptor C related to Neurotransmitter D release."
   - This suggests a connection between Receptor C and the release of Neurotransmitter D.

2. The sentence: "Binding of ligand E to Receptor C modulates the release of Neurotransmitter D in synaptic clefts."
   - This statement explicitly states that when ligand E binds to Receptor C, it influences how much Neurotransmitter D is released.
   - This indicates that Receptor C is indeed involved in regulating or affecting the release of Neurotransmitter D.

3. Since the sentence clearly shows a relationship between Receptor C and the release of Neurotransmitter D, it provides direct support for the triple.

**Final Answer:**
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Supplement F related to Muscle Growth" receive at least indirect support from the statement: "Participants taking Supplement F showed increased protein synthesis rates post-exercise."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple: "Supplement F related to Muscle Growth."
   - This suggests a connection between taking Supplement F and muscle growth.

2. The statement: "Participants taking Supplement F showed increased protein synthesis rates post-exercise."
   - Protein synthesis is a key physiological process that underlies muscle repair and hypertrophy (growth) after exercise.
   - While the statement does not explicitly mention "muscle growth," increased protein synthesis rates in a post-exercise context are commonly linked to muscle recovery and growth over time.

3. Since protein synthesis is a critical step in the process of building muscle, an increase in protein synthesis rates can be considered an indirect indicator that Supplement F supports or is related to muscle growth.

**Final Answer:**
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Is the triple "Factor G related to Cell Cycle Regulation" directly or indirectly supported by the sentence: "Overexpression of Factor G disrupts normal cell cycle progression, leading to uncontrolled cell proliferation."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple: "Factor G related to Cell Cycle Regulation."  
   - This means we need to see if Factor G influences or is involved in controlling the cell cycle.

2. The provided sentence:  
   "Overexpression of Factor G disrupts normal cell cycle progression, leading to uncontrolled cell proliferation."

3. Analysis:  
   - The sentence explicitly states that when Factor G is overexpressed, it disrupts normal cell cycle progression.  
   - Disrupting normal cell cycle progression is a direct indication that Factor G affects how the cell cycle is regulated.  
   - Since cell cycle progression is a key part of cell cycle regulation, this sentence clearly links Factor G to the regulation of the cell cycle.

**Conclusion:**  
The sentence provides direct support for the triple, confirming that Factor G is related to cell cycle regulation.

**Final Answer:**  
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Does the phrase "Compound H related to Liver Toxicity" receive at least indirect support from the statement: "Exposure to Compound H has been associated with elevated liver enzymes in clinical studies."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple: "Compound H related to Liver Toxicity."  
   - This implies Compound H is associated with harmful effects on the liver.

2. The statement:  
   "Exposure to Compound H has been associated with elevated liver enzymes in clinical studies."

3. Analysis:  
   - Elevated liver enzymes (such as ALT, AST) are commonly used as indicators of liver injury or stress.
   - Although the statement does not explicitly say "toxicity," elevated liver enzymes strongly suggest liver damage or impairment.
   - Therefore, the statement provides at least indirect evidence that Compound H is related to liver toxicity, as these elevated enzymes typically reflect liver dysfunction.

**Conclusion:**  
Since elevated liver enzymes are a known biomarker for liver damage, the sentence indirectly supports the connection between Compound H and liver toxicity.

**Final Answer:**  
Answer: Yes
    ```
    ---
    **USER:**
    ```
    'Is the triple "Molecule I related to Inflammatory Response" directly or indirectly supported by the sentence: "Molecule I acts as a key mediator in the inflammatory response during infection."?'
    ```
    
    **ASSISTANT:**
    ```
    **Step-by-step reasoning:**

1. The triple is: "Molecule I related to Inflammatory Response."
   - This suggests that Molecule I should have some connection with the inflammatory response.

2. The given sentence:
   "Molecule I acts as a key mediator in the inflammatory response during infection."

3. Analysis:
   - The sentence explicitly states that Molecule I is a "key mediator" in the inflammatory response.
   - Being a "key mediator" directly places Molecule I in a central role in the inflammatory response process.

4. Conclusion:
   - The sentence provides direct support for the triple, as it clearly states Molecule I is involved in the inflammatory response.

**Final Answer:**
Answer: Yes
    ```
    ---
    
            USER: ('\'Does the phrase "{triple}" receive at least indirect support from the statement: "{sentence}"?',).
    
            ASSISTANT:

    '''
    """

        return prompt


class ExperimentRunner:
    """Runs experiments using RAG."""

    def __init__(self, dataset_name, rag_processor):
        self.dataset_name = dataset_name
        self.rag_processor = rag_processor

    def run(self, experiment_name):
        try:
            dataset = langfuse.get_dataset(self.dataset_name)
            if not dataset:
                logging.error(f"Dataset {self.dataset_name} could not be retrieved.")
                return

            for idx, item in enumerate(dataset.items, 1):
                try:
                    completion, prompt, response_content = (
                        self.rag_processor.process_triple(
                            item.input["triple"], item.input["sentence"]
                        )
                    )

                    generation = langfuse.generation(
                        name=experiment_name,
                        input=prompt,
                        output=response_content,
                        model=self.rag_processor.model,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                    )
                    item.link(generation, experiment_name)

                    generation.score(
                        name="exact_match", value=item.expected_output in completion
                    )
                except KeyError as e:
                    logging.exception(f"Missing key in item {idx}: {e}")
                except Exception as e:
                    logging.exception(f"Error processing item {idx}: {e}")

            logging.info(f"Experiment '{experiment_name}' completed.")
        except Exception as e:
            logging.error(f"Error running experiment '{experiment_name}': {e}")


if __name__ == "__main__":
    Logger.setup_logging()

    try:
        load_dotenv()
        openai_api_key = config("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_api_key)

        rag_processor = RAGProcessor(
            openai_client=client,
            model="gpt-4o-mini",
        )

        dataset_manager = DatasetManager()
        local_items = dataset_manager.load_local_dataset(
            "./json/local_items_single_3.json"
        )

        dataset_name = "RAG_biomedical_factchecks_human_yes_without_semmed__6"
        dataset = dataset_manager.get_dataset(dataset_name)

        if not dataset:
            logging.info(
                f"Dataset {dataset_name} not found. Creating and uploading dataset..."
            )
            with open("./json/local_items_single_3.json", "r") as file:
                local_items = json.load(file)
            dataset_manager.create_dataset(dataset_name)
            dataset_manager.upload_items_to_langfuse(dataset_name, local_items)
        else:
            logging.info(f"Dataset {dataset_name} exists. Starting experiment...")

         
        experiment_runner = ExperimentRunner(
            dataset_name=dataset_name,
            rag_processor=rag_processor,
        )
        experiment_name = (
            f"exp_{datetime.now().strftime('%m_%d_%Y__%H_%M_%S')}__human_labeled"
        )
        experiment_runner.run(experiment_name)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


