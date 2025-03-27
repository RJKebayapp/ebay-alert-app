
import postmark
from postmark import PMMail
import os

POSTMARK_API_KEY = os.getenv("POSTMARK_API_KEY")  # Make sure to set this environment variable

def send_registration_email(email: str):
    message = PMMail(
        subject="Please confirm your registration",
        to=email,
        sender="no-reply@example.com",  # Change this to your email address
        html_body="<html><body><h1>Welcome!</h1><p>Thanks for registering. Please confirm your email address.</p></body></html>"
    )
    try:
        message.send()
    except Exception as e:
        print(f"Error sending email: {e}")
