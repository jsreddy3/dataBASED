import openai
import json
import time
import os

openai.api_key = os.environ.get('OPENAI_API_KEY')
HIGH_LEVEL_OVERVIEW = "You are being used as a tool to help in a project allowing users to transform numerous pages of unstructured text data into a queryable database. In order to do this, the user uploads lots of individual files, each of the same classification. They then describe the nature of the file, and in conversation with you, they identify fields by which the file can be summarized in a database. For example, they might upload the text of an insurance report and together, you and the user might, in conversation, identify the fields of customer, company, insurance claim type, etc. Your current task: "

def start_conversation(document_content, user_input):
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

def call_openai(messages, function_info=None, max_retries=1, wait_time=1):
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