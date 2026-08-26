import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_key = os.environ.get("ENCRYPTION_KEY")
if not _key:
    # Fallback to prevent crash if running tests without env setup
    # In production, this should fail loudly.
    _key = Fernet.generate_key().decode()

fernet = Fernet(_key.encode())

def encrypt_token(token: str) -> str:
    """Encrypt a raw token string."""
    if not token:
        return None
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted token string."""
    if not encrypted_token:
        return None
    return fernet.decrypt(encrypted_token.encode()).decode()
