from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64

from cryptography.hazmat.primitives import hashes


encryptor = None


def init_encrypt(init_key, salt):
    global encryptor
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(init_key.encode()))
    encryptor = Fernet(key)
    return salt


def encrypt(plaintext):
    return encryptor.encrypt(plaintext.encode())


def decipher(ciphertext):
    return encryptor.decrypt(ciphertext).decode()
