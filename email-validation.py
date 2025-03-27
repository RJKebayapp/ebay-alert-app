from email_validator import validate_email, EmailNotValidError

def validate(email):
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        raise ValueError("Invalid email")
    return email
