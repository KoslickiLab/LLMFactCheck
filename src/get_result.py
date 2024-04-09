
def get_result(model_info, prompt, model_type):
    """
    Get a result from a specified model.

    Args:
        model_info (tuple or object): Information about the model, including the model itself and optional context.
        prompt (str): The text prompt for the model.
        model_type (str): The type of the model being used.

    Returns:
        str: The generated result text.

    """
    if model_type.startswith('llama'):
        # If using a Llama model

        if isinstance(model_info, tuple):
            # If the Llama model has additional context
            model, context = model_info
            full_prompt= prompt,
            
        else:
            # If using a standalone Llama model
            model = model_info
            full_prompt = prompt
        prompt = full_prompt
        prompt_template=f'''SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. When responding, please start with 'Yes' or 'No' to directly address the query posed. Follow this with a comprehensive justification of your decision, integrating relevant scientific knowledge, the specifics of the case at hand, and any potential implications or nuances that may influence the interpretation of the evidence provided.           

        USER: {prompt}

        ASSISTANT:

        '''
        prompt_chunks = [prompt_template]
        result_text = ""
        for chunk in prompt_chunks:
            # Interact with the Llama model
            chunk=f'''"SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. When responding, please start with 'Yes' or 'No' to directly address the query posed. Follow this with a comprehensive justification of your decision, integrating relevant scientific knowledge, the specifics of the case at hand, and any potential implications or nuances that may influence the interpretation of the evidence provided.            

        USER: ('\'Is the triple ""Phase related to Follicle stimulating hormone measurement"" directly or indirectly supported by the sentence: ""In pre-menopause healthy females, blood was sampled weekly during one menstruation cycle and menstruation phases (follicular, ovulatory, luteal) were determined by FSH/LH levels.""?',)

        ASSISTANT:

        ""SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. When responding, please start with 'Yes' or 'No' to directly address the query posed. Follow this with a comprehensive justification of your decision, integrating relevant scientific knowledge, the specifics of the case at hand, and any potential implications or nuances that may influence the interpretation of the evidence provided.            

        USER: ('\'Is the triple ""Phase related to DNA chemical synthesis"" directly or indirectly supported by the sentence: ""The influence of amlodipine on VSMC growth/proliferation was studied by measuring DNA synthesis and cell number under experimental conditions, which allowed us to determine the cell cycle phase in which amlodipine exerts its effects.""?',)

        ASSISTANT:

        ""SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. When responding, please start with 'Yes' or 'No' to directly address the query posed. Follow this with a comprehensive justification of your decision, integrating relevant scientific knowledge, the specifics of the case at hand, and any potential implications or nuances that may influence the interpretation of the evidence provided.            

        USER: ('\'Is the triple ""Phase related to Sodium measurement"" directly or indirectly supported by the sentence: ""Based on a biophysical photoreceptor model, the Na(+)- and Ca(2+)-currents and concentration changes were determined from the first transient depolarization phase of the photoreceptor response.""?',)

        ASSISTANT:

        ""SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. When responding, please start with 'Yes' or 'No' to directly address the query posed. Follow this with a comprehensive justification of your decision, integrating relevant scientific knowledge, the specifics of the case at hand, and any potential implications or nuances that may influence the interpretation of the evidence provided.            

        USER: ('\'Is the triple ""Phase related to Bronchoalveolar Lavage"" directly or indirectly supported by the sentence: ""Challenge of the airways of sensitized guinea pigs with aerosolized ovalbumin resulted in an early phase of microvascular protein leakage and a delayed phase of eosinophil accumulation in the airway lumen, as measured using bronchoalveolar lavage (BAL).""?',)

        ASSISTANT:

        ""SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. When responding, please start with 'Yes' or 'No' to directly address the query posed. Follow this with a comprehensive justification of your decision, integrating relevant scientific knowledge, the specifics of the case at hand, and any potential implications or nuances that may influence the interpretation of the evidence provided.            

        USER: ('\'Is the triple ""Phase related to Flash"" directly or indirectly supported by the sentence: ""The threshold for a brief flash (the probe) was measured at various phases on a background that was varied sinusoidally in time.""?',)

        ASSISTANT:

        "'''
            print(chunk)
            try:
                response = model(prompt=chunk, max_tokens=1024, temperature=0.8,
                             top_p=0.95, repeat_penalty=1.2, top_k=150, echo=False)
                result_text += response["choices"][0]["text"]

            except Exception as error:
                result_text += str(error)
            
            print(result_text)
        return result_text, prompt_template

    else:
        # If using an OpenAI model

        return get_result_from_openai(model_info, prompt, model_type)


def get_result_from_openai(model_info, prompt, model_type):
    """
    Get a result from an OpenAI model.

    Args:
        model_info (tuple or object): Information about the OpenAI model, including the model itself and optional context.
        prompt (str): The text prompt for the model.
        model_type (str): The type of the OpenAI model being used.

    Returns:
        str: The generated result text.

    """
    if 'icl' in model_type:
        # If using an OpenAI model with Integrated Conversation Learning (ICL)

        client, (model, context) = model_info
        full_prompt = context + '\n' + prompt
    else:
        # If using a standard OpenAI model
        client, model = model_info
        full_prompt = prompt

    try:
        # Make a request to the OpenAI model
        json_request = {
            "model": model,
            "messages": [{"role": "user", "content": full_prompt}]
        }

        response = client.chat.completions.create(**json_request)
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None
