import openai
import json
import time
import os

openai.api_key = os.environ.get('OPENAI_API_KEY')
HIGH_LEVEL_OVERVIEW = "You are being used as a tool to help in a project allowing users to transform numerous pages of unstructured text data into a queryable database. In order to do this, the user uploads lots of individual files, each of the same classification. They then describe the nature of the file, and in conversation with you, they identify fields by which the file can be summarized in a database. For example, they might upload the text of an insurance report and together, you and the user might, in conversation, identify the fields of customer, company, insurance claim type, etc. After that, you are used to identify information from each file which fits within the given field and return a completed structured dictionary with information from each field. The user will then give feedback on your structured dictionary for three or four examples. Once the user has finalized those examples, you will run over all documents and create a structured format for them all. Your current task: "

def start_conversation(document_content, user_input):
    """
    Begins conversation with model to identify fields in document.
    
    Parameters:
    - document_content (str): Uploaded document content.
    - user_input (str): User's description of the document.
    
    Returns:
    - Dictionary of fields, descriptions, and a natural language response.
    """

    # Initial function call to identify fields
    system_message = {
        "role": "system",
        "content": HIGH_LEVEL_OVERVIEW + "Read this document and the user's description of the document type. Identify possible fields by which to summarize the document."
    }
    user_message = {
        "role": "user",
        "content": user_input + " " + document_content
    }
    messages = [system_message, user_message]

    # Function info
    function_info = [{
        "name": "identify_fields",
        "description": "Identify potential fields from the provided text",
        "parameters": {
            "type": "object",
            "properties": {
                "fields": {"type": "array", "items": {"type": "string"}},
                "descriptions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["fields", "descriptions"]
        }
    }]
    
    # Get fields and descriptions from the function call
    fields_data = call_openai(messages, function_info)
    
    # Update the system message for natural language response
    system_message["content"] = HIGH_LEVEL_OVERVIEW + "Provide a natural language response based on the identified fields and the ongoing conversation."
    
    # Now, create a natural language response
    nl_response = call_openai(messages + [{"role": "assistant", "content": json.dumps(fields_data)}])
    
    response = {
        "fields": fields_data.get("fields", []),
        "descriptions": fields_data.get("descriptions", []),
        "naturalResponse": nl_response
    }
    
    return response


def refine_fields(session_data, user_input):
    """
    Refines identified fields based on user feedback.
    
    Parameters:
    - session_data (dict): Data from the current user session.
    - user_input (str): User's feedback.
    
    Returns:
    - Dictionary of refined fields, descriptions, and a natural language response.
    """

    # Build the system and user messages with session data
    system_message = {
        "role": "system",
        "content": HIGH_LEVEL_OVERVIEW + "Using the document uploaded and the fields provided, refine the field suggestions based on prior interactions. Do not repeat fields that have already been confirmed or rejected."
    }
    
    # Adding prior conversation and fields for context
    conversation_history = "\n".join(session_data.get('conversation_history', []))
    suggested_fields = ", ".join(session_data.get('suggested_fields', []))
    confirmed_fields = ", ".join(session_data.get('confirmed_fields', []))
    rejected_fields = ", ".join(session_data.get('rejected_fields', []))
    document_content = session_data.get('document_content', '')
    
    user_message = {
        "role": "user",
        "content": f"{user_input} Prior conversation: {conversation_history}. Confirmed fields: {confirmed_fields}. Rejected fields: {rejected_fields}. Suggested fields: {suggested_fields}. Document content: {document_content}"
    }

    # Function info
    function_info = [{
        "name": "identify_fields",
        "description": "Identify potential fields from the provided text",
        "parameters": {
            "type": "object",
            "properties": {
                "fields": {"type": "array", "items": {"type": "string"}},
                "descriptions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["fields", "descriptions"]
        }
    }]
    
    messages = [system_message, user_message]
    
    # Get refined fields and descriptions from the function call
    fields_data = call_openai(messages, function_info)
    
    # Update the system message for natural language response
    system_message["content"] = HIGH_LEVEL_OVERVIEW + "Provide a natural language response based on the refined fields, prior interactions, and the ongoing conversation."
    
    # Now, create a natural language response with the refined fields
    nl_response = call_openai(messages + [{"role": "assistant", "content": json.dumps(fields_data)}])
    
    response = {
        "fields": fields_data.get("fields", []),
        "descriptions": fields_data.get("descriptions", []),
        "naturalResponse": nl_response
    }
    
    return response

def doc_to_fields(document_content, finalized_fields, session_data, examples=[]):
    """
    Extracts field values from a document.
    
    Parameters:
    - document_content (str): Document content.
    - finalized_fields (list): Fields to extract.
    - session_data (dict): Current user session data.
    - examples (list, optional): Previous field mappings.
    
    Returns:
    - Dictionary mapping fields to extracted values.
    """

    # Filtering out the current document from the examples, if it exists.
    examples = [example for example in examples if example['document'] != document_content]

    # Preparing the function calling structure for extracting all fields
    function_info = {
        "name": "extract_field_values",
        "description": "Extract the values for the given fields from the provided document.",
        "parameters": {
            "type": "object",
            "properties": {field: {"type": "string"} for field in finalized_fields},
            "required": finalized_fields
        }
    }

    # Message structure
    system_message = {
        "role": "system",
        "content": HIGH_LEVEL_OVERVIEW + "Given the entire conversation history, extract the values for the provided fields from the document."
    }
    
    conversation_history = "\n".join(session_data.get('conversation_history', []))
    confirmed_fields = ", ".join(session_data.get('confirmed_fields', []))
    rejected_fields = ", ".join(session_data.get('rejected_fields', []))
    suggested_fields = ", ".join(session_data.get('suggested_fields', []))
    
    user_message = {
        "role": "user",
        "content": f"{conversation_history} Confirmed fields: {confirmed_fields}. Rejected fields: {rejected_fields}. Suggested fields: {suggested_fields}. Document content: {document_content}"
    }
    
    messages = [system_message, user_message]

    # Call to OpenAI API
    fields_mapping = call_openai(messages, function_info)

    return fields_mapping



def call_openai(messages, function_info=None, max_retries=1, wait_time=1):
    """
    Communicates with OpenAI API for results.
    
    Parameters:
    - messages (list): Messages modeling a conversation.
    - function_info (dict, optional): Info about a function for the model.
    - max_retries (int, optional): API retries. Default is 1.
    - wait_time (int, optional): Time between retries. Default is 1s.
    
    Returns:
    - Results from the OpenAI API.
    """

    functions = [function_info] if function_info else []
    
    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
                functions=functions
            )
            if function_info:
                function_call = response.choices[0].message.get('function_call', {})
                if function_call:
                    return json.loads(function_call['arguments'])
            else:
                return response.choices[0].message.get('content', "")
        except json.JSONDecodeError:
            retries += 1
            time.sleep(wait_time)
    
    raise Exception("Maximum retries reached. API issues.")