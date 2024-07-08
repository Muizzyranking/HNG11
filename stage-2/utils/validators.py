from .models import User


def validate_user_data(data):
    errors = []
    required_fields = ['firstName', 'lastName', 'email', 'password']

    for field in required_fields:
        if field not in data or not data[field]:
            errors.append({"field": field, "message": f"{field} is required"})

    if 'email' in data and not is_valid_email(data['email']):
        errors.append({"field": "email", "message": "Invalid email"})

    if 'email' in data and User.query.filter_by(email=data['email']).first():
        errors.append({"field": "email", "message": "Email already exists"})

    return errors


def is_valid_email(email):
    import re
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, email)
