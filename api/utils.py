import secrets
from django.core.mail import send_mail
from django.conf import settings


def generate_otp() -> str:
    """Generate a secure 6-digit numeric OTP."""
    return f"{secrets.randbelow(900000) + 100000}"


def send_otp_email(email: str, otp: str, purpose: str) -> None:
    """Send an OTP email to the user."""
    if purpose == 'registration':
        subject = "Notes App - Verify Your Account"
        message = (
            f"Welcome to Notes App!\n\n"
            f"Your verification code is: {otp}\n\n"
            f"This code will expire in 10 minutes.\n"
            f"If you did not request this, please ignore this email."
        )
    elif purpose == 'forgot_password':
        subject = "Notes App - Password Reset Code"
        message = (
            f"Hello,\n\n"
            f"We received a request to reset your password for your Notes App account.\n\n"
            f"Your password reset code is: {otp}\n\n"
            f"This code will expire in 10 minutes.\n"
            f"If you did not request a password reset, please ignore this email."
        )
    else:
        subject = "Notes App - Verification Code"
        message = f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes."

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Notes App <noreply@notesapp.com>')
    send_mail(subject, message, from_email, [email], fail_silently=False)
