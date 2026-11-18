# ArchivioCrypto

Desktop application prototype for encrypting ZIP archives into `.acrypt` containers and restoring them.

## Features
- Python + PySide6 desktop GUI
- Italian / English interface
- Light / dark themes
- AES-256-GCM authenticated encryption
- Scrypt password-based key derivation
- Chunked file processing (bounded memory use)
- ZIP integrity test before restoring the output
- Original files are not overwritten

## Requirements
- Python 3.10+
- Dependencies in `requirements.txt`

## Run from source
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Build a portable application
Build on each target operating system; PyInstaller is not a universal cross-compiler.

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --name ArchivioCrypto main.py
```

The application will be in `dist/ArchivioCrypto/` (one-folder build). To create a single-file build, add `--onefile`.

## Security and format notes
- `.acrypt` format version 1 uses a fixed Scrypt parameter set (N=32768, r=8, p=1), a random 16-byte salt, a random 12-byte GCM nonce, and a 16-byte GCM tag.
- The fixed header is authenticated as AES-GCM additional authenticated data.
- The full ciphertext is authenticated before the decrypted ZIP is moved into place.
- Do not lose the password: there is no recovery mechanism.
- Keep a separate backup of important archives.
- This is a development prototype, not a security-audited product. Have the format and implementation independently reviewed before distributing it for sensitive data.
- Secure deletion of temporary files is not guaranteed on SSDs, journaled filesystems, or copy-on-write storage.

## Installer packaging
Create and test native packages separately on Windows, macOS, and Linux. For macOS distribution outside your own machine, code signing and notarization may be required. For Linux, AppImage and distribution-specific packages can be prepared from a Linux build environment.
