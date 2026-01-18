import os
import io
import json
import secrets
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, send_file
from flask_session import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import database

# --- Configuration ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Google OAuth Config
# NOTE: Ensure 'credentials.json' is present in the root directory.
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

# Check if credentials file exists
if not os.path.exists(CLIENT_SECRETS_FILE):
    # If not, checks for example and warns
    if os.path.exists("credentials.json.example"):
        print("WARNING: 'credentials.json' not found. Please rename 'credentials.json.example' and add your keys.")
    else:
        print("WARNING: 'credentials.json' not found.")

def get_authenticated_service():
    if 'credentials' not in session:
        return None
    
    creds_data = session['credentials']
    creds = Credentials(**creds_data)
    
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

@app.before_first_request
def startup():
    database.init_db()

@app.route('/')
def index():
    if 'credentials' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authorize')
def authorize():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return "Error: credentials.json not found on server.", 500

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    
    # Ideally should be dynamic based on deployment
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'credentials' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# --- API Endpoints ---

@app.route('/api/files')
def get_files():
    if 'credentials' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        service = get_authenticated_service()
        # List files: name, size, mimeType
        results = service.files().list(
            pageSize=50, fields="nextPageToken, files(id, name, mimeType, size)").execute()
        items = results.get('files', [])
        
        # Cache metadata in DB (Optional enhancement - implemented basically here)
        conn = database.get_db_connection()
        for item in items:
            conn.execute('''
                INSERT OR REPLACE INTO file_cache (id, name, mime_type, size, last_modified)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['id'], item['name'], item['mimeType'], item.get('size'), '')) 
        conn.commit()
        conn.close()

        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/download/<file_id>')
def download_file(file_id):
    if 'credentials' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        service = get_authenticated_service()
        file_meta = service.files().get(fileId=file_id).execute()
        name = file_meta.get('name', 'downloaded_file')
        
        request_drive = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request_drive)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return send_file(fh, as_attachment=True, download_name=name)
        
    except Exception as e:
         return jsonify({'error': str(e)}), 500

@app.route('/api/sync/upload', methods=['POST'])
def upload_file():
    if 'credentials' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        service = get_authenticated_service()
        
        # Save temp file for upload
        temp_path = os.path.join('/tmp', file.filename)
        file.save(temp_path)
        
        file_metadata = {'name': file.filename}
        media = MediaFileUpload(temp_path, resumable=True)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({'status': 'success', 'fileId': file.get('id')})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Localhost for dev
    # On Heroku/Netlify, this would be handled by a WSGI runner (gunicorn)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # For local testing only!
    app.run(debug=True, port=5000)
