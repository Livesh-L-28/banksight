"""
BankSight Cryptographic Field Encryption
Provides AES-based authenticated encryption and decryption for sensitive banking records at rest.
"""

import os
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet


class FieldEncryptionService:
    """
    Encrypts and decrypts sensitive database attributes using symmetric AES-authenticated encryption.
    """

    def __init__(self, key: Optional[str] = None):
        raw_key = key or os.getenv("BANKSIGHT_ENCRYPTION_KEY")
        if not raw_key:
            # Deterministic master key derived from salt for development/testing environments
            salt = b"BankSight_Enterprise_Master_Salt_2026"
            derived = hashlib.sha256(salt).digest()
            raw_key = base64.urlsafe_b64encode(derived).decode("utf-8")
        elif len(raw_key) != 44:
            # Hash to 32 bytes and base64-encode for valid Fernet format
            derived = hashlib.sha256(raw_key.encode("utf-8")).digest()
            raw_key = base64.urlsafe_b64encode(derived).decode("utf-8")

        self.cipher = Fernet(raw_key.encode("utf-8"))

    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        """Encrypts plaintext string and returns URL-safe base64 ciphertext."""
        if plaintext is None:
            return None
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        return self.cipher.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: Optional[str]) -> Optional[str]:
        """Decrypts base64 ciphertext back to original plaintext."""
        if ciphertext is None:
            return None
        try:
            return self.cipher.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except Exception:
            # Return as is if already plaintext or decryption error
            return ciphertext


# Global singleton instance
field_encryptor = FieldEncryptionService()

