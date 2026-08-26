import logging

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, body: str):
    """
    Mock email sender for Phase 10.
    In Phase 11, this will be replaced with a real email provider (e.g. Resend, SendGrid, SMTP).
    """
    # Print securely to console for development verification
    border = "=" * 50
    print(f"\n{border}")
    print(f"?? EMAIL MOCK TRIGGERED")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print(f"{border}\n")
    
    logger.info(f"Sent mock email to {to_email} with subject: {subject}")
    return True
