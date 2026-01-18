# CloudSync Dashboard

A responsive web application for managing and syncing files across cloud services, starting with Google Drive. Features IT-centric analytics, file management, and secure OAuth authentication.

## Features

- **User Authentication**: Secure Login/Logout via Google OAuth 2.0.
- **Cloud Integration**: Real-time integration with Google Drive API.
- **Visual Dashboard**:
    - Interactive Pie Chart for file type distribution.
    - Bar Chart for top largest files.
- **File Management**:
    - List all files with metadata (Name, Type, Size).
    - One-click Download.
    - Upload files directly to Google Drive.
- **Responsive Design**: Built with Bootstrap 5 for mobile and desktop.
- **Caching**: SQLite database for caching file metadata (scaffolded).

## Prerequisites

- Python 3.8+
- Google Cloud Platform Account (for API credentials)

## Installation

1.  **Clone/Download the repository**.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Google Credentials**:
    - Go to [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Enable **Google Drive API**.
    - Configure OAuth Consent Screen.
    - Create Credentials (OAuth Client ID) -> Select "Web Application".
        - Add `http://localhost:5000` to **Authorized JavaScript origins**.
        - Add `http://localhost:5000/oauth2callback` to **Authorized redirect URIs**.
    - Download the JSON file, rename it to `credentials.json`, and place it in the project root.
    > *Note: A `credentials.json.example` is provided for reference.*

## Usage

1.  **Run the Application**:
    ```bash
    python app.py
    ```
2.  **Access Dashboard**:
    - Open your browser and navigate to `http://localhost:5000`.
    - Click "Sign in with Google".
    - Grant permissions to view specific files.
3.  **Explore**:
    - View charts analyzing your Drive usage.
    - Download files via the action buttons.
    - Upload new files using the "Upload File" button.

## Deployment Notes

- **Heroku (Backend)**:
    - Create a `Procfile`: `web: gunicorn app:app`.
    - Set config vars for `SECRET_KEY`.
    - Ensure `credentials.json` is securely added (e.g., via environment variables or secure build files).
- **Netlify (Frontend)**:
    - Not applicable directly as this is a server-side rendered Flask app. For a decoupled architecture, you would host the `templates` converted to React/Vue on Netlify and point to the Heroku API.

## License

This project is licensed under the MIT License.
