# Move Attachments - Smartsheet Integration

## Overview

This project provides a Flask-based web application to facilitate the secure transfer of attachments between Smartsheet sheets. The application interacts with the Smartsheet API to verify, download, and upload attachments while ensuring data integrity and access control.

**Note:** Using the **moveattachments** script does not make a straight move, it takes the attchment from the source and adds it into the target row and then it deletes the original file from the source once the process is complete. 

## Features

- 🔑 **Secure API authentication** using API keys and session tokens.
- 📁 **Fetch, verify, and transfer attachments** between Smartsheet sheets.
- 🔄 **Retry logic with exponential backoff** for API reliability.
- 🔐 **Secure access token management** via Flask sessions.
- 🌐 **Web-based user interface** for easy interaction.

## Installation

### **1. Install Python**

Ensure you have **Python 3.8+** installed.

- **Windows**: Download from [Python.org](https://www.python.org/downloads/) and install.
- **macOS/Linux**:
  ```sh
  sudo apt install python3  # Ubuntu/Debian
  brew install python       # macOS
  ```

### **2. Install Required Packages**

Run the following command to install dependencies:

```sh
pip install -r requirements.txt
```

### **3. Set Up Environment Variables**

Create a `.env` file in the root directory and add:

```ini
FLASK_SECRET_KEY=your_secret_key
API_ACCESS_KEY=your_api_key
```

## Usage

### **1. Run the Application**

To Copy attachments, start the Flask app with:

```sh
python copyattachments.py
```

To Move attachments, start the Flask app with:

```sh
python moveattachments.py
```

The app will be accessible at:

```
http://127.0.0.1:5000
```

### **2. Enter Smartsheet API Access Token**

- Enter your Smartsheet API Access Token on the homepage.

### **3. Verify Attachments**

- Provide **Source Sheet ID** and **Target Sheet ID**.
- Click **Verify** to check attachments for transfer.

### **4. Transfer Attachments**

- Select attachments to transfer.
- Click **Start** to initiate the transfer.
- If an attachment already exists, the system will prompt to upload a new version.

## API Endpoints

| Method | Endpoint                | Description                                  |
| ------ | ----------------------- | -------------------------------------------- |
| `POST` | `/set_token`            | Stores the API access token securely.        |
| `POST` | `/verify_attachments`   | Verifies which attachments need to be moved. |
| `POST` | `/transfer_attachments` | Transfers selected attachments.              |
| `POST` | `/upload_new_version`   | Uploads a new version of an existing file.   |

## Logging

📜 All API requests and errors are logged in `run_log.txt` for debugging.

## Future Enhancements

🚀 Planned improvements:

- Enhanced UI for better user experience.
- OAuth authentication for improved security.
- Advanced error handling and notifications.
- Include an option to choose the target Task Name instead of using an exact match to increase use-cases.

## Contributing

Pull requests are welcome! If you have suggestions, open an issue first to discuss proposed changes.

## License

This project is **not licensed** for public use. If you intend to use or modify it, please contact the author for permission.

---

*✨ Happy coding! ✨*

