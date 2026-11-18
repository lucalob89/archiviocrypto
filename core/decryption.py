import os
import tempfile
import zipfile
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .crypto_utils import (
    MAGIC, SALT_SIZE, NONCE_SIZE, TAG_SIZE, CHUNK_SIZE, derive_key
)

HEADER_SIZE = len(MAGIC) + SALT_SIZE + NONCE_SIZE

def decrypt_zip(input_file, output_file, password, progress=None, cancelled=None):
    source = Path(input_file)
    destination = Path(output_file)

    if not source.is_file():
        raise FileNotFoundError(str(source))
    if destination.exists():
        raise FileExistsError(str(destination))
    if source.resolve() == destination.resolve():
        raise ValueError("Input and output files must be different.")

    total_size = source.stat().st_size
    temp_path = None
    try:
        with source.open("rb") as encrypted:
            header = encrypted.read(HEADER_SIZE)
            if len(header) != HEADER_SIZE or header[:len(MAGIC)] != MAGIC:
                raise ValueError("Unrecognized or invalid ArchivioCrypto file.")

            salt_start = len(MAGIC)
            salt = header[salt_start:salt_start + SALT_SIZE]
            nonce = header[-NONCE_SIZE:]

            ciphertext_size = total_size - HEADER_SIZE - TAG_SIZE
            if ciphertext_size < 0:
                raise ValueError("Encrypted file is truncated.")

            encrypted.seek(-TAG_SIZE, os.SEEK_END)
            tag = encrypted.read(TAG_SIZE)
            if len(tag) != TAG_SIZE:
                raise ValueError("Authentication tag is missing.")

            key = derive_key(password, salt)
            decryptor = Cipher(
                algorithms.AES(key), modes.GCM(nonce, tag)
            ).decryptor()
            decryptor.authenticate_additional_data(header)
            encrypted.seek(HEADER_SIZE)

            with tempfile.NamedTemporaryFile(
                mode="wb", dir=str(destination.parent), prefix=".acrypt-",
                suffix=".tmp", delete=False
            ) as temp:
                temp_path = Path(temp.name)
                remaining = ciphertext_size
                processed = 0
                while remaining:
                    if cancelled and cancelled():
                        raise InterruptedError("Operation cancelled.")
                    chunk = encrypted.read(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        raise ValueError("Encrypted file is truncated.")
                    remaining -= len(chunk)
                    processed += len(chunk)
                    temp.write(decryptor.update(chunk))
                    if progress:
                        progress(int(processed * 100 / max(ciphertext_size, 1)))

                # GCM verifies the password and the authenticity of all ciphertext.
                temp.write(decryptor.finalize())
                temp.flush()
                os.fsync(temp.fileno())

        # Validate the ZIP only after GCM authentication succeeded.
        if not zipfile.is_zipfile(temp_path):
            raise ValueError("Decrypted data is not a valid ZIP archive.")
        with zipfile.ZipFile(temp_path, "r") as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise ValueError(f"ZIP integrity check failed: {bad_member}")

        if destination.exists():
            raise FileExistsError(str(destination))
        os.replace(temp_path, destination)
        temp_path = None
        if progress:
            progress(100)
        return str(destination)

    except InvalidTag:
        raise ValueError("Wrong password or encrypted file has been modified.")
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
