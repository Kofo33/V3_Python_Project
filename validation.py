import re

EMAIL_VALIDATE_PATTERN: str = r"^\S+@\S+\.\S+$"
PASSWORD_VALIDATE_PATTERN: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{16,}$"


def validate_email(mail: str) -> bool:
    if re.match(EMAIL_VALIDATE_PATTERN, mail):
        return True
    else:
        return False


def validate_password(password: str) -> bool:
    """
    Regex pattern for a strong password:
    - At least 16 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character from the specified set
    :param password:
    :return: bool
    """
    if re.match(PASSWORD_VALIDATE_PATTERN, password):
        return True
    else:
        return False
