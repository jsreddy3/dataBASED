import openai
import json
import time
import os

# Set the API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Pre-defined examples (we'll fill this in soon)
examples = [
    # Example format:
    # {
    #     'sales_call': 'example sales call text',
    #     'structured_output': {
    #         'Meeting Date': '',
    #         'Client': '',
    #         # ... other fields ...
    #     }
    # }
]

def analyze_content(content, max_retries=1, wait_time=1):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that looks at semi-structured or unstructured text pages and identifies potential fields by which they could be condensed for future use in a database. I'd like a list of fields, descriptions, and a natural language response for the conversation to continue."
        }
    ]

    # Add the examples to the messages
    for example in examples:
        example['structured_output'] = json.dumps(example['structured_output'])
        messages.extend([
            {"role": "user", "content": example['content']},  
            {"role": "assistant", "content": example['structured_output']}
        ])

    # Add the new content to the messages
    messages.append({"role": "user", "content": content})

    # Update the function definition to match the structured output you want
    functions = [
        {
            "name": "identify_fields",
            "description": "Identify potential fields from the provided text",
            "parameters": {
                "type": "object",
                "properties": {
                    "fields": {"type": "array", "items": {"type": "string"}},
                    "descriptions": {"type": "array", "items": {"type": "string"}},
                    "naturalResponse": {"type": "string"}
                },
                "required": ["fields", "descriptions", "naturalResponse"]
            }
        }
    ]

    retries = 0
    while retries < max_retries:
        try:
            print("Sending the following messages to OpenAI:", messages)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
                functions=functions
            )
            print("Received response from OpenAI:", response.choices[0].message)
            function_call = response.choices[0].message.get('function_call', {})
            
            # Since there isn't a real function to execute, 
            # just return the arguments of the function call as the result.
            if function_call:
                arguments = json.loads(function_call['arguments'])
                response_data = {
                    'function_call': {
                        'name': 'identify_fields',
                        'arguments': arguments
                    }
                }
                return response_data
            
        except json.JSONDecodeError:
            print("Error decoding JSON. Response received:", response)
            retries += 1
            time.sleep(wait_time)

    raise Exception("Maximum number of retries reached. The API may be experiencing issues.")