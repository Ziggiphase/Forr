import aiosmtplib
from email.message import EmailMessage
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_verification_email(to_email: str, token: str):
    subject = "Verify your account for Forr"
    # Construct a verification link. In a real app, this should be the frontend URL.
    # We will use the frontend URL since the user will click it and it will call our API or handle it in the frontend.
    verify_url = f"http://localhost:3000/verify-email?token={token}"
    
    body = f"""
    Welcome to Forr!
    
    Please verify your email address by clicking the link below:
    {verify_url}
    
    If you did not sign up for this account, please ignore this email.
    """

    smtp_host = getattr(settings, "smtp_host", None)
    smtp_port = getattr(settings, "smtp_port", 587)
    smtp_user = getattr(settings, "smtp_user", None)
    smtp_password = getattr(settings, "smtp_password", None)
    
    if not all([smtp_host, smtp_user, smtp_password]):
        logger.warning(f"SMTP configuration is incomplete. Printing email content to console instead.")
        logger.warning(f"Verification Email to {to_email}:\n{body}")
        return

    message = EmailMessage()
    message["From"] = getattr(settings, "smtp_from_email", "noreply@forr.com")
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            use_tls=False,
            start_tls=True,
        )
        logger.info(f"Verification email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        # We don't raise the exception to prevent signup from failing just because email failed,
        # but in production we might want to handle this differently.
