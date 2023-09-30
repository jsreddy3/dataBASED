from flask import Flask, request, render_template, jsonify, session
from converters import convert_to_txt
from gpt_helper import start_conversation, refine_fields, doc_to_fields
import os
import pandas as pd
import openai

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf', 'html'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('file')

        for file in files:
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                safe_filename = filename.rsplit('.', 1)[0] + '.txt'
                if file.filename.rsplit('.', 1)[1].lower() != 'txt':
                    converted_content = convert_to_txt(file)
                    with open(safe_filename, 'w') as txt_file:
                        txt_file.write(converted_content)
                else:
                    file.save(safe_filename)
    return render_template('upload.html')

@app.route('/get_files', methods=['GET'])
def get_files():
    uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    return jsonify({"files": uploaded_files})

@app.route('/get_file_content', methods=['POST'])
def get_file_content():
    try:
        # Get the file name from the request
        file_name = request.json.get('file_name')
        
        # Ensure the file name is provided and exists in the upload folder
        if not file_name or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], file_name)):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        # Read the file content
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name), 'r') as file:
            content = file.read()
        
        return jsonify({"status": "success", "file_name": file_name, "content": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/select_file', methods=['POST'])
def select_file():
    selected_file = request.json.get('selected_file', str())
    document_content = ""
    if selected_file:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], selected_file), 'r') as file:
            document_content = file.read()
    session['document_content'] = document_content
    return jsonify({"status": "success", "selected_file": selected_file, "document_content": document_content})

@app.route('/initiate_conversation', methods=['POST'])
def initiate_conversation():
    user_input = request.json.get('user_input')
    document_content = session['document_content']
    session['confirmed_fields'] = set()
    session['rejected_fields'] = set()
    session['conversation_history'] = [user_input]

    response = start_conversation(document_content, user_input)
    
    session['suggested_fields'] = set(response['fields'])
    session['conversation_history'].append(response["naturalResponse"])

    return jsonify(response)

@app.route('/handle_user_message', methods=['POST'])
def handle_user_message():
    user_input = request.json.get('user_input')
    session['conversation_history'].append(user_input)
    
    response = refine_fields(session, user_input)
    
    # Update the suggested fields based on the response
    new_suggested_fields = set(response['fields'])
    session['suggested_fields'] |= new_suggested_fields
    session['suggested_fields'] -= session['confirmed_fields']
    session['suggested_fields'] -= session['rejected_fields']
    
    session['conversation_history'].append(response["naturalResponse"])

    return jsonify(response)

@app.route('/swap_document', methods=['POST'])
def swap_document():
    try:
        # Get the new document name from the request
        document_name = request.json.get('document_name')
        
        # Load the new document content
        document_path = os.path.join(app.config['UPLOAD_FOLDER'], document_name)
        with open(document_path, 'r') as doc_file:
            session['document_content'] = doc_file.read()

        # Clear or update any other session data related to the previous document if necessary
        # For instance, you might want to reset or retain suggested_fields, confirmed_fields, etc.

        return jsonify({"status": "success", "message": f"Switched to document: {document_name}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/modify_fields', methods=['POST'])
def modify_fields():
    confirmed_fields = set(request.json.get('confirmed_fields', []))
    rejected_fields = set(request.json.get('rejected_fields', []))
    suggested_fields = set(request.json.get('suggested_fields', []))

    session['confirmed_fields'] |= confirmed_fields
    session['confirmed_fields'] -= (rejected_fields)
    
    session['rejected_fields'] |= rejected_fields
    session['rejected_fields'] -= (confirmed_fields | suggested_fields)
    
    session['suggested_fields'] |= suggested_fields
    session['suggested_fields'] -= (confirmed_fields | rejected_fields)

    # Return the updated fields to the client
    return jsonify({
        "confirmed_fields": list(session['confirmed_fields']),
        "rejected_fields": list(session['rejected_fields']),
        "suggested_fields": list(session['suggested_fields'])
    })


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@app.route('/get_confirmed_fields', methods=['GET'])
def get_confirmed_fields():
    return jsonify({"confirmed_fields": list(session.get('confirmed_fields', set()))})

@app.route('/get_rejected_fields', methods=['GET'])
def get_rejected_fields():
    return jsonify({"rejected_fields": list(session.get('rejected_fields', set()))})

@app.route('/get_suggested_fields', methods=['GET'])
def get_suggested_fields():
    return jsonify({"suggested_fields": list(session.get('suggested_fields', set()))})

@app.route('/get_examples', methods=['GET'])
def get_examples():
    return jsonify({"examples": session.get('examples', {})})

# Updated complete_doc_fields with error handling
@app.route('/complete_doc_fields', methods=['POST'])
def complete_doc_fields():
    try:
        document_name = request.json.get('document_name')
        document_path = os.path.join(app.config['UPLOAD_FOLDER'], document_name)
    
        with open(document_path, 'r') as doc_file:
            document_content = doc_file.read()
    
        fields_mapping = doc_to_fields(document_content, session.get('examples', []))
    
        # Format for the response
        response_data = {
            "document_name": document_name,
            "document_content": document_content,
            "fields_mapping": fields_mapping
        }

        # We might want to store the initial mapping for the document in the session for reference
        if 'initial_mappings' not in session:
            session['initial_mappings'] = {}
        session['initial_mappings'][document_name] = fields_mapping
    
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_mappings', methods=['POST'])
def update_mappings():
    refined_output = request.json.get('refined_output')
    document_name = refined_output.get('document_name')

    # Replace the existing example with the refined one
    if 'examples' not in session:
        session['examples'] = {}
    session['examples'][document_name] = refined_output

    return jsonify({"status": "success", "message": "Example updated."})


@app.route('/bulk_process', methods=['POST'])
def bulk_process_documents():
    try:
        processed_data = []
        
        # Iterate through all uploaded documents
        for document_name in os.listdir(app.config['UPLOAD_FOLDER']):
            document_path = os.path.join(app.config['UPLOAD_FOLDER'], document_name)
            
            with open(document_path, 'r') as doc_file:
                document_content = doc_file.read()
            
            # Extract field values using the finalized fields and examples
            fields_mapping = doc_to_fields(document_content, session.get('confirmed_fields', []), session, examples=session.get('examples', []))
            processed_data.append(fields_mapping)
        
        return jsonify({"status": "success", "data": processed_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save_to_excel', methods=['POST'])
def save_to_excel():
    try:
        # Get processed data (you could also call the bulk_process_documents function here)
        response = bulk_process_documents()
        processed_data = response.json.get('data', [])

        # Convert to DataFrame
        df = pd.DataFrame(processed_data)

        # Save to Excel
        excel_path = "/path/to/save/excel/file.xlsx"  # Modify this path as required
        df.to_excel(excel_path, index=False)

        return jsonify({"status": "success", "message": f"Data saved to {excel_path}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
