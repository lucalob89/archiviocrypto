import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC = b"ACRYPT01"
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
CHUNK_SIZE = 1024 * 1024

# Parameters are stored in the file header in a future format revision.
# Version 1 fixes these parameters and authenticates the complete header.
SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1

def derive_key(password: str, salt: bytes) -> bytes:
    if not password:
        raise ValueError("Password cannot be empty.")
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
    )
    return kdf.derive(password.encode("utf-8"))

def make_header():
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    return MAGIC + salt + nonce, salt, nonce
