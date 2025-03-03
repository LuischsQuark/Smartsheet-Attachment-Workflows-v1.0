from flask import Flask, render_template, request, jsonify, session
import requests
import os
import traceback
import time
from functools import wraps

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # Secure session key

LOG_FILE = "run_log.txt"
MATCH_COLUMN_INDEX = 0
API_KEY = os.getenv("API_ACCESS_KEY", "my_secure_api_key")  # API key for authentication

# Logging function
def log_message(message):
    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")

# Authentication decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("API-Key") != API_KEY:
            return jsonify({"error": "Unauthorized access"}), 403
        return f(*args, **kwargs)
    return decorated_function

# Store access token securely
@app.route('/set_token', methods=['POST'])
@require_api_key
def set_token():
    data = request.json
    session['ACCESS_TOKEN'] = data.get("accessToken")
    if not session['ACCESS_TOKEN']:
        return jsonify({"error": "Access token is required"}), 400
    return jsonify({"message": "Access token set successfully!"})

# Retry logic for API requests with exponential backoff
def make_request(method, url, headers, **kwargs):
    max_retries = 3
    delay = 2
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_message(f"API request failed: {e}, attempt {attempt + 1}/{max_retries}")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
    return None

# Fetch attachments securely
def get_attachments(sheet_id):
    access_token = session.get('ACCESS_TOKEN')
    if not access_token:
        return []
    url = f"https://api.smartsheet.com/2.0/sheets/{sheet_id}/attachments"
    headers = {"Authorization": f"Bearer {access_token}"}
    return make_request("GET", url, headers).get('data', [])

# Fetch rows securely
def get_rows(sheet_id):
    access_token = session.get('ACCESS_TOKEN')
    url = f"https://api.smartsheet.com/2.0/sheets/{sheet_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    return make_request("GET", url, headers).get('rows', [])

# Find row in target sheet
def find_row_by_column_value(column_value, rows):
    for row in rows:
        cells = row.get('cells', [])
        if len(cells) > MATCH_COLUMN_INDEX and cells[MATCH_COLUMN_INDEX].get('value') == column_value:
            return row['id']
    return None
    
# Download attachment
def download_attachment(sheet_id, attachment_id):
    access_token = session.get('ACCESS_TOKEN')
    if not access_token:
        return []
    url = f"https://api.smartsheet.com/2.0/sheets/{sheet_id}/attachments/{attachment_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    return response.content

# Upload attachment to row
def upload_attachment_to_row(sheet_id, row_id, file_name, file_content, file_type):
    access_token = session.get('ACCESS_TOKEN')
    if not access_token:
        return []
    url = f"https://api.smartsheet.com/2.0/sheets/{sheet_id}/rows/{row_id}/attachments"
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {'file': (file_name, file_content, file_type)}
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()    
    
    
@app.route('/')
def index():
    return render_template('index.html')  # Explicitly render the index.html

@app.route('/verify_attachments', methods=['POST'])
@require_api_key
def verify_attachments():
    try:
        data = request.json
        source_sheet_id = data.get('sourceSheetId')
        target_sheet_id = data.get('targetSheetId')
        
        attachments = get_attachments(source_sheet_id)
        source_rows = get_rows(source_sheet_id)
        target_rows = get_rows(target_sheet_id)
        
        verified_attachments = []
        for attachment in attachments:
            file_name = attachment.get('name')
            source_row_id = attachment.get('parentId')
            source_row = next((row for row in source_rows if row['id'] == source_row_id), None)
            
            if source_row:
                column_value = source_row.get('cells', [{}])[0].get('value', 'Unknown')
                target_row_id = find_row_by_column_value(column_value, target_rows)
                if target_row_id:
                    verified_attachments.append({
                        "attachmentId": attachment['id'],
                        "attachmentName": file_name,
                        "version": attachment.get('version', 'N/A'),
                        "sourceSheetName": source_sheet_id,
                        "sourceTaskName": column_value,
                        "destinationTaskName": column_value,  # Ensuring source task maps correctly
                        "destinationSheetName": target_sheet_id
                    })
        
        return jsonify({"attachments": verified_attachments})
    except Exception as e:
        log_message(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
        
# Check if attachment exists in the target row
def check_attachment_exists(sheet_id, row_id, file_name):
    log_message(f"Checking if attachment '{file_name}' exists in row {row_id} of sheet {sheet_id}...")
    attachments = get_attachments(sheet_id)
    for attachment in attachments:
        if attachment.get('parentId') == row_id and attachment.get('name').strip().lower() == file_name.strip().lower():
            log_message(f"FOUND: Attachment '{file_name}' already exists with ID {attachment['id']}")
            return attachment['id']
    log_message(f"NOT FOUND: Attachment '{file_name}' does not exist in row {row_id} of sheet {sheet_id}.")
    return None
        
# Function to upload a new version of an existing attachment
def upload_attachment_version(sheet_id, attachment_id, file_name, file_content, file_type):
    access_token = session.get('ACCESS_TOKEN')
    if not access_token:
        return []
    if not file_name or not file_content:
        log_message("ERROR: Missing file name or content for version upload.")
        return None

    url = f"https://api.smartsheet.com/2.0/sheets/{sheet_id}/attachments/{attachment_id}/versions"
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file": (file_name, file_content, file_type)}
    
    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        log_message(f"SUCCESS: Uploaded new version of {file_name} in sheet {sheet_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        log_message(f"ERROR: Failed to upload new version of {file_name}: {e}")
        log_message(f"API Response: {response.text if 'response' in locals() else 'No response received'}")
        return None

@app.route('/upload_new_version', methods=['POST'])
@require_api_key
def upload_new_version():
    try:
        data = request.json
        target_sheet_id = data.get('targetSheetId')
        attachment_id = data.get('attachmentId')
        file_name = data.get('fileName')

        if not file_name:
            log_message("ERROR: file_name is missing from request payload! Attempting to retrieve from source.")
            attachments = get_attachments(target_sheet_id)
            matching_attachment = next((att for att in attachments if att['id'] == attachment_id), None)
            if matching_attachment:
                file_name = matching_attachment.get('name')
                log_message(f"Retrieved file name from source: {file_name}")

        log_message(f"Attempting to upload new version: File Name: {file_name}, Attachment ID: {attachment_id}, Sheet ID: {target_sheet_id}")

        if not file_name or not attachment_id:
            log_message("ERROR: Missing file name or attachment ID.")
            return jsonify({"error": "Missing file name or attachment ID."}), 400

        file_content = download_attachment(target_sheet_id, attachment_id)

        if not file_content:
            log_message("ERROR: Failed to download file content.")
            return jsonify({"error": "Failed to download file content."}), 400

        response = upload_attachment_version(target_sheet_id, attachment_id, file_name, file_content, 'application/octet-stream')

        if response:
            return jsonify({"message": "New version uploaded successfully!"})
        else:
            return jsonify({"error": "Failed to upload new version."}), 500
    except Exception as e:
        log_message(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/transfer_attachments', methods=['POST'])
@require_api_key
def transfer_attachments():
    try:
        data = request.json
        selected_attachments = data.get('attachments', [])
        target_sheet_id = data.get('targetSheetId')
        source_sheet_id = data.get('sourceSheetId')
        target_rows = get_rows(target_sheet_id)
        
        for attachment in selected_attachments:
            attachment_id = attachment['attachmentId']
            file_name = attachment.get('attachmentName')
            destination_task_name = attachment['destinationTaskName']
            
            if not file_name:
                log_message(f"ERROR: Missing file name for attachment ID {attachment_id}")
                continue
            
            file_content = download_attachment(source_sheet_id, attachment_id)
            log_message(f"Downloaded: {file_name}")
            
            target_row_id = find_row_by_column_value(destination_task_name, target_rows)
            
            if not target_row_id:
                log_message(f"ERROR: Target row not found for {destination_task_name}")
                continue
            
            existing_attachment_id = check_attachment_exists(target_sheet_id, target_row_id, file_name)
            
            if existing_attachment_id:
                log_message(f"Attachment exists. Prompting UI for new version upload: {file_name}")
                return jsonify({"prompt": "Attachment already exists. Upload a new version?", "attachmentId": existing_attachment_id, "fileName": file_name})
            
            response = upload_attachment_to_row(target_sheet_id, target_row_id, file_name, file_content, 'application/octet-stream')
            log_message(f"SUCCESS: Uploaded {file_name} to row {target_row_id} in sheet {target_sheet_id}")
        
        return jsonify({"message": "Process completed successfully!"})
    except Exception as e:
        log_message(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
