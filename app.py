from flask import Flask, request, redirect, url_for, render_template, jsonify
from converters import convert_to_txt
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf', 'html'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaded_files = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            safe_filename = filename.rsplit('.', 1)[0] + '.txt'  # Construct .txt filename
            if file.filename.rsplit('.', 1)[1].lower() != 'txt':
                converted_content = convert_to_txt(file)
                with open(safe_filename, 'w') as txt_file:
                    txt_file.write(converted_content)
            else:
                file.save(safe_filename)

            # Append the filename to the uploaded_files list
            uploaded_files.append(safe_filename)
    return render_template('upload.html')

@app.route('/get_files', methods=['GET'])
def get_files():
    # Returns a list of all the uploaded files
    print(uploaded_files)
    return jsonify({"files": uploaded_files})

@app.route('/select_files', methods=['POST'])
def select_files():
    selected_files = request.json.get('selected_files', [])
    # For demonstration purposes, let's grab the first selected file's content
    first_file_content = ""
    if selected_files:
        with open(selected_files[0], 'r') as file:
            first_file_content = file.read()
    return jsonify({"status": "success", "selected_files": selected_files, "first_file_content": first_file_content})


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
