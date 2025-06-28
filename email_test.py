import os
import json
import requests

# --- START: SendPulse API Functions (Copied from your send_email.py for this test) ---

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
    sender_name,
    receiver_email,
    subject,
    html_content_file,
    api_id,
    api_secret
):
    """
    Sends an HTML email using SendPulse API.
    """
    try:
        if not os.path.exists(html_content_file):
            print(f"Error: HTML file '{html_content_file}' not found.")
            return

        with open(html_content_file, 'r', encoding='utf-8') as f:
            html_body = f.read()

        access_token = get_sendpulse_access_token(api_id, api_secret)
        if not access_token:
            print("Failed to obtain SendPulse access token. Cannot send email.")
            return

        if not sender_email:
            print("Error: SENDER_EMAIL is missing.")
            return
        if not receiver_email:
            print("Error: RECEIVER_EMAIL is missing.")
            return

        send_email_url = "https://api.sendpulse.com/smtp/emails"
        send_email_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        email_data = {
            "html": html_body,
            "text": "Please enable HTML to view this email.",
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
        response.raise_for_status()

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

# --- END: SendPulse API Functions ---

# --- TEST CONFIGURATION (HARDCODED FOR LOCAL TEST) ---
# !!! REPLACE THESE WITH YOUR ACTUAL CREDENTIALS AND EMAILS !!!
TEST_SENDPULSE_API_ID = "81f8ec7f01e05acc67d897878e0959c3"
TEST_SENDPULSE_API_SECRET = "04a26510e771af184fc0a388e313f530"
TEST_SENDER_EMAIL = "karthick840@yahoo.in" # Must be verified in SendPulse!
TEST_SENDER_NAME = "My Test Sender"
TEST_RECEIVER_EMAIL = "karthick840@gmail.com" # Can be the same as sender for testing
TEST_EMAIL_SUBJECT = "Local Test: Your Latest Product Offers"
TEST_HTML_FILE_PATH = "generated_email.html" # Ensure this file exists relative to your script

# --- Run the test ---
print("Initiating local email test...")
send_html_email_sendpulse(
    sender_email=TEST_SENDER_EMAIL,
    sender_name=TEST_SENDER_NAME,
    receiver_email=TEST_RECEIVER_EMAIL,
    subject=TEST_EMAIL_SUBJECT,
    html_content_file=TEST_HTML_FILE_PATH,
    api_id=TEST_SENDPULSE_API_ID,
    api_secret=TEST_SENDPULSE_API_SECRET
)
print("Local email test finished attempt.")