# Attachment Workflows - Smartsheet Integration

## Overview
This project provides a Flask-based web application to facilitate the secure transfer of attachments between Smartsheet sheets. The application interacts with the Smartsheet API to verify, download, and upload attachments while ensuring data integrity and access control.

## Features
- Secure API authentication using API keys and session tokens.
- Fetch, verify, and transfer attachments between Smartsheet sheets.
- Implements retry logic with exponential backoff for API reliability.
- Securely manages access tokens via Flask sessions.
- Provides a web-based interface for user interaction.

## Requirements
This project requires **Python 3.8+** and the following dependencies:

### Install Python (if needed)
- **Windows**: Download from [Python.org](https://www.python.org/downloads/) and install.
- **macOS/Linux**:
  ```sh
  sudo apt install python3  # Ubuntu/Debian
  brew install python       # macOS
  ```

### Install Required Packages
Run the following command to install all dependencies:
```sh
pip install -r requirements.txt
```

### Required Environment Variables
Create a `.env` file in the root directory and define the following environment variables:
```ini
FLASK_SECRET_KEY=your_secret_key
API_ACCESS_KEY=your_api_key
```

## Usage
### 1. Run the Application
To start the Flask app to Copy Attachments, run:
```sh
python copyattachments.py
```

To start the Flask app to Move Attachments, run:
```sh
python moveattachments.py
```

The app will start in debug mode and can be accessed in a web browser at:
```
http://127.0.0.1:5000
```

### 2. Enter Smartsheet API Access Token
- Enter your Smartsheet API Access Token on the homepage.

### 3. Verify Attachments
- Provide **Source Sheet ID** and **Target Sheet ID**.
- Click **Verify** to check attachments for transfer.

### 4. Transfer Attachments
- Select attachments to transfer.
- Click **Start** to initiate the transfer.
- If an attachment already exists, the system will prompt to upload a new version.

## API Endpoints
### `POST /set_token`
Stores the Smartsheet API Access Token securely in the session.

### `POST /verify_attachments`
Verifies which attachments need to be transferred.

### `POST /transfer_attachments`
Transfers selected attachments from the source sheet to the target sheet.

### `POST /upload_new_version`
Uploads a new version of an existing attachment.

## Logging
- API requests and errors are logged in `run_log.txt`.
- Logs can be reviewed for debugging purposes.

## Future Enhancements
- Implement UI improvements.
- Add OAuth authentication for better security.
- Improve error handling and notifications.

## License
This project is licensed under the MIT License.

