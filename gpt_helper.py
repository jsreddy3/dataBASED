import openai
import json
import time
import os

openai.api_key = os.environ.get('OPENAI_API_KEY')
HIGH_LEVEL_OVERVIEW = "You are being used as a tool to help in a project allowing users to transform numerous pages of unstructured text data into a queryable database. In order to do this, the user uploads lots of individual files, each of the same classification. They then describe the nature of the file, and in conversation with you, they identify fields by which the file can be summarized in a database. For example, they might upload the text of an insurance report and together, you and the user might, in conversation, identify the fields of customer, company, insurance claim type, etc. Your current task: "

def start_conversation(document_content, user_input):
    """
    Short Explanation:
    - Initiates a conversation with the model to identify potential fields in the given document.
  
    Parameters:
    - document_content (str): The content of the document that the user uploaded.
    - user_input (str): The user's description or context about the document type.
  
    Return Values:
    - A dictionary containing:
      - fields: A list of potential fields identified from the document.
      - descriptions: A list of descriptions or context about the identified fields.
      - naturalResponse: A natural language response from the model about the identified fields.
    
    Usage:
    - Called by the main application (e.g., Flask route) when a user uploads a document and provides a description. 
      Used to start the process of identifying fields in the document.
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
    Short Explanation:
    - Refines the identified fields based on the ongoing conversation and feedback from the user.
  
    Parameters:
    - session_data (dict): Contains data from the current user session including document content, 
      conversation history, and lists of confirmed, rejected, and suggested fields.
    - user_input (str): The user's feedback or additional information about refining the fields.
  
    Return Values:
    - A dictionary containing:
      - fields: A list of refined fields after taking into account user feedback.
      - descriptions: A list of descriptions or context about the refined fields.
      - naturalResponse: A natural language response from the model about the refined fields.
    
    Usage:
    - Called by the main application after initial fields have been suggested and the user provides feedback. 
      Used to refine and improve the field suggestions based on user input.
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

def doc_to_fields(document_content, finalized_fields, examples=[]):
    """
    Uses the OpenAI API to extract field values from a given document.
    
    Parameters:
    - document_content (str): The content of the document from which fields are to be extracted.
    - finalized_fields (list): List of fields that have been finalized and need values extracted.
    - examples (list, optional): List of existing examples of documents and their field mappings.
    
    Return Values:
    - A dictionary mapping field names to their extracted values from the document.
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
        "content": HIGH_LEVEL_OVERVIEW + "Extract the values for the provided fields from the given document."
    }
    user_message = {
        "role": "user",
        "content": document_content
    }
    messages = [system_message, user_message]

    # Call to OpenAI API
    fields_mapping = call_openai(messages, function_info)

    return fields_mapping


def call_openai(messages, function_info=None, max_retries=1, wait_time=1):
    """
    Short Explanation:
    - Interfaces with the OpenAI API to either perform a function call or get a natural language response.
  
    Parameters:
    - messages (list): A list of message objects (dicts) that model a conversation. Each message object has a 
      role ("system", "user", or "assistant") and content (the message content).
    - function_info (dict, optional): Contains information about a function that the model should perform. 
      If not provided, a natural language response is expected from the model.
    - max_retries (int, optional): Number of retries in case of API issues. Default is 1.
    - wait_time (int, optional): Time to wait between retries. Default is 1 second.
  
    Return Values:
    - If function_info is provided: A dictionary containing the results of the function call.
    - If function_info is not provided: A string containing the model's natural language response.
    
    Usage:
    - A utility function used internally by other functions like start_conversation and refine_fields to 
      communicate with the OpenAI API and get results.
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