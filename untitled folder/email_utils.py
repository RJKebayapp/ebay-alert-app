
from postmark.models import SendEmailRequest
from postmark import ApiClient
from postmark.apis.sending_api_api import SendingAPIApi

def send_registration_email(email: str):
    # Create a new email request
    email_request = SendEmailRequest(
        From="your-email@example.com",  # Your "from" email
        To=email,  # Recipient's email
        Subject="Welcome to eBay Alerts",
        TextBody="Please verify your email by clicking the link below.",
        HtmlBody="<html><body><p>Please verify your email by clicking the link below.</p></body></html>",
        Tag="welcome-email"  # Optional tag to identify the email
    )

    # Send the email
    api_client = ApiClient(configuration)
    sending_api = SendingAPIApi(api_client)
    response = sending_api.send_email(email_request)

    return response
