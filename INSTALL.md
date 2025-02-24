
# Installation Guide for Slash

Welcome to the installation guide for **Slash**. Follow these steps to set up the environment and run the application.

---

## Prerequisites

Ensure you have the following installed:

1. **Python 3.8+**
2. **Git**

## Step 1: Clone the Repository

Clone the repository from GitHub. Open a terminal and run:

```bash
git clone https://github.com/SE-Fall-2024-Team-69/slash.git
cd slash
git checkout main
```

## Step 2: Set Up a Virtual Environment (Optional)

Creating a virtual environment is recommended to manage dependencies. Run the following:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

Install all required dependencies listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Step 4: Google OAuth Setup

1. **Google OAuth Client Secrets**: Make sure you have a valid Google OAuth client secrets file.
2. Place your client secrets JSON file at:
   ```
   C:\Users\Desmond\Desktop\slash\src\client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json
   ```

## Step 5: Configure Environment Variables

In the project root directory, create a `.env` file for environment-specific variables.

Example `.env` file contents:

```plaintext
set FLASK_APP=.\src\modules\app 
FLASK_ENV=development
GOOGLE_CLIENT_SECRET_PATH=C:\Users\Desmond\Desktop\slash\src\client_secret_92320207172-8cnk4c9unfaa7llua906p6kjvhnvkbqd.apps.googleusercontent.com.json
```

## Step 6: Run the Application

After setting up the environment and dependencies, start the Flask application:

```bash
flask run
```

By default, the app will run at `http://127.0.0.1:5000/`.

## Step 7: Additional Configuration

1. **CSV File Management**: The application manages user credentials and wishlist data in CSV files located under `src/users/`.
2. Ensure your CSV files follow the correct structure to avoid errors in data handling.

## Troubleshooting

- **Database Issues**: If the app cannot locate or read CSV files, verify the file paths and permissions.
- **OAuth Errors**: Check that your OAuth credentials are valid and stored at the specified location.

---

This guide should help you set up the development environment from the main branch. For any further assistance, please consult the project documentation or reach out to the development team.