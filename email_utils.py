import os
import postmark
from dotenv import load_dotenv

load_dotenv()

POSTMARK_TOKEN = os.getenv("POSTMARK_TOKEN", "4815cb10-234b-40fd-b407-e48790f30fc2")

def send_registration_email(to_email: str):
    try:
        client = postmark.PMMail(
            api_key=POSTMARK_TOKEN,
            subject="Welcome to the eBay 'Buy It Now' Alert App!",
            sender="noreply@yourdomain.com",
            to=to_email,
            text_body="Thank you for registering with the eBay Alert App. You're now ready to start receiving alerts!",
            tag="registration-confirmation"
        )
        client.send()
        print(f"Confirmation email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
