# Google Drive API Setup Guide

To get your "CloudSync Dashboard" working, you need to provide a `credentials.json` file. This tells Google that this app is allowed (by you) to talk to Google Drive.

## Step 1: Create a Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click the project dropdown (top left) and initiate a **New Project**.
3.  Name it `CloudSync Dashboard` and click **Create**.

## Step 2: Enable Google Drive API
1.  In the sidebar, go to **APIs & Services > Library**.
2.  Search for **"Google Drive API"**.
3.  Click on it and click **Enable**.

## Step 3: Configure OAuth Consent Screen
1.  Go to **APIs & Services > OAuth consent screen**.
2.  Choose **External** (unless you have a Google Workspace organization, then Internal is fine). Click **Create**.
3.  **App Information**:
    - App name: `CloudSync Dashboard`
    - User support email: (Select your email)
    - Developer contact information: (Enter your email)
4.  Click **Save and Continue** through the "Scopes" section (no special scopes needed here strictly for the consent screen setup itself, but the app uses `.../auth/drive`).
5.  **Test Users**: Add your own Google email address as a test user. This is critical for testing without verification.

## Step 4: Create Credentials
1.  Go to **APIs & Services > Credentials**.
2.  Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
3.  **Application type**: Select **Web application**.
4.  **Authorized JavaScript origins**:
    - Add: `http://localhost:5000`
5.  **Authorized redirect URIs**:
    - Add: `http://localhost:5000/oauth2callback`
6.  Click **Create**.

## Step 5: Download and Placement
1.  A popup will appear with your Client ID and Secret.
2.  Click the **DOWNLOAD JSON** button (it looks like a download icon).
3.  **Rename** the downloaded file to `credentials.json`.
4.  **Move** this file into the `CloudSync Dashboard` folder (where `app.py` is).

## Step 6: Run the App
1.  Run the `run.sh` script or type `python3 app.py`.
2.  Go to `http://localhost:5000`.
3.  The login should now work!
