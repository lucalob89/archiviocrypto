import os
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .crypto_utils import (
    CHUNK_SIZE, TAG_SIZE, derive_key, make_header
)

def encrypt_zip(input_file, output_file, password, progress=None, cancelled=None):
    source = Path(input_file)
    destination = Path(output_file)

    if not source.is_file():
        raise FileNotFoundError(str(source))
    if destination.exists():
        raise FileExistsError(str(destination))
    if source.resolve() == destination.resolve():
        raise ValueError("Input and output files must be different.")

    total = source.stat().st_size
    header, salt, nonce = make_header()
    key = derive_key(password, salt)

    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    encryptor.authenticate_additional_data(header)

    temp_path = None
    processed = 0
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=str(destination.parent), prefix=".acrypt-",
            suffix=".tmp", delete=False
        ) as temp:
            temp_path = Path(temp.name)
            temp.write(header)
            with source.open("rb") as original:
                while True:
                    if cancelled and cancelled():
                        raise InterruptedError("Operation cancelled.")
                    chunk = original.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    temp.write(encryptor.update(chunk))
                    processed += len(chunk)
                    if progress:
                        progress(int(processed * 100 / max(total, 1)))
                temp.write(encryptor.finalize())
                temp.write(encryptor.tag)
                temp.flush()
                os.fsync(temp.fileno())

        # Do not overwrite an existing destination.
        if destination.exists():
            raise FileExistsError(str(destination))
        os.replace(temp_path, destination)
        temp_path = None
        if progress:
            progress(100)
        return str(destination)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
