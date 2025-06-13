# app.py - Your Python Flask Backend for GitHub OAuth

from flask import Flask, redirect, url_for, request, session, render_template_string
import requests
import os

app = Flask(__name__)
# Secret key is essential for Flask sessions.
# In a real application, use a strong, randomly generated key and store it securely.
app.secret_key = os.urandom(24)

# --- GitHub OAuth Configuration ---
# IMPORTANT: Replace these with your actual Client ID and Client Secret
# obtained from your GitHub OAuth App registration.
# You MUST replace 'YOUR_GITHUB_CLIENT_ID' and 'YOUR_GITHUB_CLIENT_SECRET' below
# with your actual values from your GitHub OAuth application.
GITHUB_CLIENT_ID = "YOUR_GITHUB_CLIENT_ID" # <-- REPLACE THIS WITH YOUR CLIENT ID
GITHUB_CLIENT_SECRET = "YOUR_GITHUB_CLIENT_SECRET" # <-- REPLACE THIS WITH YOUR CLIENT SECRET

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API = "https://api.github.com/user"

# --- Root Route: Serves the HTML frontend ---
@app.route('/')
def index():
    # This route will serve the HTML login page.
    # It checks if the user is already logged in (has 'github_token' in session)
    # and displays either a login button or user info.
    if 'github_token' in session:
        return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Logged In</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    body { font-family: 'Inter', sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                    .container { background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); padding: 32px; text-align: center; max-width: 400px; width: 100%; }
                    .button { padding: 10px 20px; background-color: #ef4444; color: white; font-weight: 600; border-radius: 8px; border: none; cursor: pointer; transition: background-color 0.2s ease-in-out; }
                    .button:hover { background-color: #dc2626; }
                </style>
            </head>
            <body class="bg-gray-100 flex items-center justify-center min-height: 100vh; p-4">
                <div class="container">
                    <h2 class="text-3xl font-bold text-gray-800 mb-4">Logged In!</h2>
                    <p class="text-gray-700 text-lg mb-6">Welcome, {{ session['github_username'] }}!</p>
                    <a href="/logout" class="button">Logout</a>
                </div>
            </body>
            </html>
        """)
    else:
        return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login with GitHub</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    body { font-family: 'Inter', sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                    .container { background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); padding: 32px; text-align: center; max-width: 400px; width: 100%; }
                    .github-button {
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        padding: 12px 24px;
                        background-color: #24292e; /* GitHub black */
                        color: white;
                        font-weight: 600;
                        border-radius: 8px;
                        border: none;
                        cursor: pointer;
                        transition: background-color 0.2s ease-in-out;
                    }
                    .github-button:hover {
                        background-color: #333;
                    }
                    .github-icon {
                        width: 24px;
                        height: 24px;
                        /* Simple inline SVG for GitHub icon */
                        fill: currentColor; /* Inherit color from parent */
                    }
                </style>
            </head>
            <body class="bg-gray-100 flex items-center justify-center min-height: 100vh; p-4">
                <div class="container">
                    <h2 class="text-3xl font-bold text-gray-800 mb-6">Login to My App</h2>
                    <a href="/login/github" class="github-button">
                        <svg class="github-icon" viewBox="0 0 16 16" version="1.1" aria-hidden="true">
                            <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.19.01-.82.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.03 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07.01 1.93.01 2.2.0 0 .1-.21.55-.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8Z"></path>
                        </svg>
                        Login with GitHub
                    </a>
                </div>
            </body>
            </html>
        """)

# --- GitHub Login Endpoint ---
@app.route('/login/github')
def github_login():
    """
    Redirects the user to GitHub's authorization page.
    """
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": url_for('github_callback', _external=True),
        "scope": "user:email" # Requesting user's email access
    }
    # You might want to add a 'state' parameter for security against CSRF attacks
    # For simplicity, it's omitted here, but recommended for production.
    return redirect(f"{GITHUB_AUTHORIZE_URL}?client_id={params['client_id']}&redirect_uri={params['redirect_uri']}&scope={params['scope']}")

# --- GitHub Callback Endpoint ---
@app.route('/github_callback')
def github_callback():
    """
    Handles the callback from GitHub after user authorization.
    Exchanges the authorization code for an access token and fetches user data.
    """
    code = request.args.get('code')
    if not code:
        # Handle error if 'code' is not present (e.g., user denied access)
        print("Error: GitHub authorization failed. Code not found in callback.")
        return "Error: GitHub authorization failed. Code not found.", 400

    # Exchange authorization code for an access token
    token_data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": url_for('github_callback', _external=True),
        "accept": "json" # Request JSON response
    }
    headers = {
        "Accept": "application/json"
    }

    token_response = requests.post(GITHUB_TOKEN_URL, data=token_data, headers=headers)
    token_json = token_response.json()

    access_token = token_json.get("access_token")
    if not access_token:
        print(f"Error getting access token: {token_json.get('error_description') or token_json}")
        return f"Error getting access token: {token_json.get('error_description') or token_json}", 500
    
    print(f"Successfully retrieved access token: {access_token[:5]}... (first 5 chars)") # Print first few chars for safety

    # Use the access token to fetch user information from GitHub API
    user_headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    user_response = requests.get(GITHUB_USER_API, headers=user_headers)
    user_data = user_response.json()

    print(f"Successfully retrieved GitHub user data: {user_data.get('login')}") # Print username

    # Store necessary user data in session (for demonstration)
    session['github_token'] = access_token
    session['github_username'] = user_data.get('login', 'Guest')
    session['github_id'] = user_data.get('id')
    session['github_email'] = user_data.get('email') # May be null if user has private email

    # Redirect to a logged-in page or the root
    return redirect('/')

# --- Logout Endpoint ---
@app.route('/logout')
def logout():
    """Clears the session and logs the user out."""
    session.pop('github_token', None)
    session.pop('github_username', None)
    session.pop('github_id', None)
    session.pop('github_email', None)
    return redirect('/')

# --- Run the Flask app ---
if __name__ == '__main__':
    # Use debug=True for development. Disable in production.
    app.run(debug=True, port=5000)
