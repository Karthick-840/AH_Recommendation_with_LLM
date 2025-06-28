import os
import json
import requests # New dependency for making HTTP requests

def get_sendpulse_access_token(api_id, api_secret):
    """
    Obtains an access token from SendPulse API.
    """
    url = "https://api.sendpulse.com/oauth/access_token"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "grant_type": "client_credentials",
        "client_id": api_id,
        "client_secret": api_secret
    })
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error getting SendPulse access token: {e}")
        return None

def send_html_email_sendpulse(
    sender_email,
    sender_name, # Added sender name for SendPulse
    receiver_email,
    subject,
    html_content_file,
    api_id,
    api_secret
):
    """
    Sends an HTML email using SendPulse API.

    Args:
        sender_email (str): The 'from' email address verified in SendPulse.
        sender_name (str): The name to display as the sender (e.g., "Your Company").
        receiver_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        html_content_file (str): The path to the HTML file containing the email body.
        api_id (str): Your SendPulse API ID.
        api_secret (str): Your SendPulse API Secret.
    """
    try:
        # Read the HTML content from the file
        if not os.path.exists(html_content_file):
            print(f"Error: HTML file '{html_content_file}' not found.")
            return

        with open(html_content_file, 'r', encoding='utf-8') as f:
            html_body = f.read()

        # Get SendPulse access token
        access_token = get_sendpulse_access_token(api_id, api_secret)
        if not access_token:
            print("Failed to obtain SendPulse access token. Cannot send email.")
            return

        # --- NEW: Validate email addresses before sending ---
        if not sender_email:
            print("Error: SENDER_EMAIL is missing. Please check your GitHub Secret 'EMAIL_SENDER_EMAIL'.")
            return
        if not receiver_email:
            print("Error: RECEIVER_EMAIL is missing. Please check your GitHub Secret 'EMAIL_RECEIVER_EMAIL'.")
            return
        # --- End NEW Validation ---

        # Send email via SendPulse API
        send_email_url = "https://api.sendpulse.com/smtp/emails"
        send_email_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Construct the email payload
        email_data = {
            "html": html_body,
            "text": "Please enable HTML to view this email.", # Fallback for text-only clients
            "subject": subject,
            "from": {
                "name": sender_name,
                "email": sender_email
            },
            "to": [
                {
                    "email": receiver_email
                }
            ]
        }

        print(f"Attempting to send email to {receiver_email} via SendPulse...")
        response = requests.post(send_email_url, headers=send_email_headers, data=json.dumps(email_data))
        response.raise_for_status() # Raise an exception for HTTP errors

        result = response.json()
        if result.get("result") and result["result"] == "success":
            print("Email sent successfully via SendPulse!")
            print(f"SendPulse Batch ID: {result.get('id')}")
        else:
            print(f"Failed to send email via SendPulse. Response: {result}")

    except requests.exceptions.RequestException as e:
        print(f"An HTTP request error occurred with SendPulse API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"SendPulse API Error Response: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred during SendPulse email sending: {e}")

# --- Retrieve Configuration from Environment Variables ---
# These variables will be set by GitHub Actions secrets
SENDPULSE_API_ID = os.environ.get("SENDPULSE_API_ID")
SENDPULSE_API_SECRET = os.environ.get("SENDPULSE_API_SECRET")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_NAME = os.environ.get("SENDER_NAME", "Your Company") # Default sender name
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
EMAIL_SUBJECT = os.environ.get("EMAIL_SUBJECT")
HTML_FILE_PATH = os.environ.get("HTML_FILE_PATH")

# Basic validation for env vars being loaded
if not all([SENDPULSE_API_ID, SENDPULSE_API_SECRET, SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_SUBJECT, HTML_FILE_PATH]):
    print("Error: Missing one or more required environment variables for SendPulse email sending.")
    print("Please ensure SENDPULSE_API_ID, SENDPULSE_API_SECRET, SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_SUBJECT, HTML_FILE_PATH are set as GitHub Secrets.")
else:
    # --- Call the function to send the email using SendPulse API ---
    print("Attempting to send email...")
    send_html_email_sendpulse(
        sender_email=SENDER_EMAIL,
        sender_name=SENDER_NAME,
        receiver_email=RECEIVER_EMAIL,
        subject=EMAIL_SUBJECT,
        html_content_file=HTML_FILE_PATH,
        api_id=SENDPULSE_API_ID,
        api_secret=SENDPULSE_API_SECRET
    )

