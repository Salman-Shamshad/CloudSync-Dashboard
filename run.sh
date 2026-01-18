#!/bin/bash

# CloudSync Dashboard Launcher

echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f "credentials.json" ]; then
    echo "WARNING: credentials.json not found!"
    echo "Please create a project in Google Cloud Console, enable Drive API,"
    echo "download the OAuth 2.0 Client credentials, and save the file as 'credentials.json' in this folder."
    echo "For now, the app will start, but login will fail."
    read -p "Press Enter to continue anyway..."
fi

echo "Starting CloudSync Dashboard..."
echo "Open http://localhost:5000 in your browser."

python3 app.py
