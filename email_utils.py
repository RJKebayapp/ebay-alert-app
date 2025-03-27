# email_utils.py

from postmark.core import PMMail
import os

def send_registration_email(recipient_email: str):
    # Get the API token and sender email from environment variables
    POSTMARK_API_TOKEN = os.getenv("POSTMARK_API_TOKEN", "your_default_api_token")
    sender_email = os.getenv("EMAIL_USERNAME", "noreply@example.com")

    # Construct the email message using PMMail
    email = PMMail(
        api_key=POSTMARK_API_TOKEN,
        subject="Registration Successful",
        sender=sender_email,
        to=recipient_email,
        text_body="Thank you for registering with our service!"
    )
    
    # Send the email and return the response (or handle errors as needed)
    response = email.send()
    return response
