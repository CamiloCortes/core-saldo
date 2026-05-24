import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes:
    key_hex = os.getenv("SESSION_ENCRYPTION_KEY")
    if not key_hex:
        raise ValueError("SESSION_ENCRYPTION_KEY is not set")
    return bytes.fromhex(key_hex)


def encrypt(data: dict) -> str:
    key = _get_key()
    iv = os.urandom(16)
    aesgcm = AESGCM(key)

    plaintext = json.dumps(data).encode("utf-8")
    encrypted = aesgcm.encrypt(iv, plaintext, None)

    ciphertext = encrypted[:-16]
    auth_tag = encrypted[-16:]

    return f"{iv.hex()}:{auth_tag.hex()}:{ciphertext.hex()}"


def decrypt(encrypted_data: str) -> dict:
    parts = encrypted_data.split(":")
    if len(parts) != 3:
        raise ValueError("Invalid encrypted_data format")

    iv_hex, auth_tag_hex, ciphertext_hex = parts
    iv = bytes.fromhex(iv_hex)
    auth_tag = bytes.fromhex(auth_tag_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)

    key = _get_key()
    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(iv, ciphertext + auth_tag, None)
    return json.loads(plaintext.decode("utf-8"))
