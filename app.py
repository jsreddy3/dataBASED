from flask import Flask, request, render_template, jsonify, session
from converters import convert_to_txt
from gpt_helper import start_conversation, refine_fields, doc_to_fields
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf', 'html'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
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

@app.route('/select_files', methods=['POST'])
def select_files():
    selected_files = request.json.get('selected_files', [])
    first_file_content = ""
    if selected_files:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], selected_files[0]), 'r') as file:
            first_file_content = file.read()
    return jsonify({"status": "success", "selected_files": selected_files, "first_file_content": first_file_content})

@app.route('/start_conversation', methods=['POST'])
def initiate_conversation():
    document_content = request.json.get('document_content')
    user_input = request.json.get('user_input')
    session['document_content'] = document_content
    session['confirmed_fields'] = []
    session['rejected_fields'] = []
    session['suggested_fields'] = []
    session['conversation_history'] = [user_input]

    response = start_conversation(document_content, user_input)
    
    session['suggested_fields'].extend(response['fields'])
    session['conversation_history'].append(response["naturalResponse"])  # Add model's response to conversation history

    return jsonify(response)

@app.route('/refine_fields', methods=['POST'])
def handle_field_refinement():
    user_input = request.json.get('user_input')
    confirmed_fields = request.json.get('confirmed_fields', [])
    rejected_fields = request.json.get('rejected_fields', [])

    # Update session's conversation history, confirmed and rejected fields
    session['conversation_history'].append(user_input)
    session['confirmed_fields'].extend(confirmed_fields)
    session['rejected_fields'].extend(rejected_fields)
    session['suggested_fields'] = list(set(session['suggested_fields']) - set(confirmed_fields + rejected_fields))
    
    response = refine_fields(session, user_input)

    session['suggested_fields'].extend(response['fields'])
    session['conversation_history'].append(response["naturalResponse"])  # Add model's response to conversation history

    return jsonify(response)

@app.route('/create_doc_fields', methods=['POST'])
def create_doc_fields():
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

@app.route('/update_examples', methods=['POST'])
def update_examples():
    refined_output = request.json.get('refined_output')
    document_name = refined_output.get('document_name')

    # Replace the existing example with the refined one
    if 'examples' not in session:
        session['examples'] = {}
    session['examples'][document_name] = refined_output

    return jsonify({"status": "success", "message": "Example updated."})



if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
