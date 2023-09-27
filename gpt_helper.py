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

# Function to use OpenAI API to analyze the content and provide potential fields
def analyze_content(content, max_retries=3, wait_time=1):
    messages = [
        {
            "role": "system", 
            "content": "You are a helpful assistant that looks at semi-structured or unstructured text pages and identifies potential fields by which they could be condensed for future use in a database."
        }
    ]

    # Add the examples to the messages
    for example in examples:
        example['structured_output'] = json.dumps(example['structured_output'])
        messages.extend([
            {"role": "user", "content": example['content']},  # content string
            {"role": "assistant", "content": example['structured_output']}  # corresponding structured output
        ])

    # Add the new content to the messages
    messages.append({"role": "user", "content": content})

    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            return_dict = response.choices[0].message['content']
            return json.loads(return_dict)
        except json.JSONDecodeError:
            retries += 1
            time.sleep(wait_time)

    raise Exception("Maximum number of retries reached. The API may be experiencing issues.")

