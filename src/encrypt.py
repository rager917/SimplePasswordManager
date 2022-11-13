from cryptography.fernet import Fernet

encryptor = None
def init_encrypt(init_key):
    encryptor = Fernet(init_key)


def encrypt(plaintext, key):
    return encryptor.encrypt(key)

def decipher(ciphertext, key):
    return encryptor.decrypt(key)