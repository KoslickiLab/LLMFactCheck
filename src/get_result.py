
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
        prompt_template=f'''
        Context: 
	USER: ('\'Is the triple "Phase related to Follicle stimulating hormone measurement" directly or indirectly supported by the sentence: "In pre-menopause healthy females, blood was sampled weekly during one menstruation cycle and menstruation phases (follicular, ovulatory, luteal) were determined by FSH/LH levels."?',)

        ASSISTANT: Yes

        USER: ('\'Is the triple "Phase related to Sodium measurement" directly or indirectly supported by the sentence: "Based on a biophysical photoreceptor model, the Na(+)- and Ca(2+)-currents and concentration changes were determined from the first transient depolarization phase of the photoreceptor response."?',)

        ASSISTANT:Yes

        USER: ('\'Is the triple "Phase related to Bronchoalveolar Lavage" directly or indirectly supported by the sentence: "Challenge of the airways of sensitized guinea pigs with aerosolized ovalbumin resulted in an early phase of microvascular protein leakage and a delayed phase of eosinophil accumulation in the airway lumen, as measured using bronchoalveolar lavage (BAL)."?',)

        ASSISTANT: Yes

        USER: ('\'Does the phrase "Ciprofloxacin related to DNA Gyrase" receive at least indirect support from the statement: "Effect of ranolazine in preventing postoperative atrial fibrillation in patients undergoing coronary revascularization surgery."?',)

        ASSISTANT: No

        USER: ('\'Does the phrase "Ciprofloxacin related to Crohn disease" receive at least indirect support from the statement: "Recent evidence of beneficial effects of ranolazine (RAN) in type II diabetes motivates interest in the role of the late sodium current (INaL) in glucose-stimulated insulin secretion."?',)

        ASSISTANT: No

        USER: ('\'Does the phrase "Ciprofloxacin related to endophthalmitis" receive at least indirect support from the statement: "Furthermore, the activated Akt/mTOR signaling pathway induced by AF was further activated by ranolazine."?',)

        ASSISTANT: No


        SYSTEM: You are a computational biologist tasked with evaluating scientific claims. Your role requires you to apply critical thinking and your expertise to interpret data and research findings accurately. Answer 'Yes' or 'No' to directly address the query posed.                 
        
        USER: {prompt}.

        ASSISTANT:

        '''
        prompt_chunks = [prompt_template]
        result_text = ""
        for chunk in prompt_chunks:
            # Interact with the Llama model
            print(chunk)
            response = model(prompt=chunk, max_tokens=1, temperature=0.8,
                             top_p=0.95, repeat_penalty=1.2, top_k=150, echo=False)
            result_text += response["choices"][0]["text"]
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
