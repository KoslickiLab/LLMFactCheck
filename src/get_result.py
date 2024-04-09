
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
