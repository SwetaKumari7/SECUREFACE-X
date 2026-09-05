import os
import pickle
import hashlib
import numpy as np

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


DATA_DIR = r"data"
MODELS_DIR = r"models"

AES_KEY_FILE = os.path.join(DATA_DIR, "aes_secret.key")
AES_TEMPLATE_FILE = os.path.join(MODELS_DIR, "face_templates_aes.enc")
AES_HASH_FILE = os.path.join(MODELS_DIR, "face_templates_aes.sha256")


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def get_or_create_aes_key():
    """Create or load a 256-bit AES key."""

    if os.path.exists(AES_KEY_FILE):
        with open(AES_KEY_FILE, "rb") as file:
            key = file.read()

        if len(key) != 32:
            raise ValueError("AES key must be exactly 32 bytes.")

        return key

    key = os.urandom(32)

    with open(AES_KEY_FILE, "wb") as file:
        file.write(key)

    return key


def encrypt_templates():
    """Encrypt biometric templates using AES-256-CBC."""

    plaintext_file = os.path.join(MODELS_DIR, "face_templates.pkl")

    if not os.path.exists(plaintext_file):
        raise FileNotFoundError(
            "face_templates.pkl was not found.\n"
            "Run train.py first if you need to regenerate templates."
        )

    with open(plaintext_file, "rb") as file:
        plaintext = file.read()

    key = get_or_create_aes_key()

    # Generate a random 16-byte initialization vector.
    iv = os.urandom(16)

    # PKCS7 padding for AES block size.
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    encryptor = cipher.encryptor()

    ciphertext = (
        encryptor.update(padded_data)
        + encryptor.finalize()
    )

    # Store IV together with ciphertext.
    encrypted_data = iv + ciphertext

    with open(AES_TEMPLATE_FILE, "wb") as file:
        file.write(encrypted_data)

    # Calculate SHA-256 hash of encrypted template.
    file_hash = hashlib.sha256(encrypted_data).hexdigest()

    with open(AES_HASH_FILE, "w") as file:
        file.write(file_hash)

    print("AES-256 encryption completed.")
    print("Encrypted template:", AES_TEMPLATE_FILE)
    print("SHA-256 hash:", AES_HASH_FILE)

    # Remove plaintext template after successful encryption.
    try:
        os.remove(plaintext_file)
        print("Plaintext biometric templates deleted.")
    except OSError as error:
        print("Warning: Could not delete plaintext template.")
        print(error)


def decrypt_templates():
    """Decrypt AES-256 encrypted biometric templates."""

    if not os.path.exists(AES_TEMPLATE_FILE):
        raise FileNotFoundError(
            "AES encrypted templates were not found."
        )

    key = get_or_create_aes_key()

    with open(AES_TEMPLATE_FILE, "rb") as file:
        encrypted_data = file.read()

    # Verify integrity before decryption.
    if os.path.exists(AES_HASH_FILE):

        with open(AES_HASH_FILE, "r") as file:
            stored_hash = file.read().strip()

        current_hash = hashlib.sha256(
            encrypted_data
        ).hexdigest()

        if current_hash != stored_hash:
            raise ValueError(
                "INTEGRITY CHECK FAILED: "
                "Encrypted biometric template was modified."
            )

        print("SHA-256 integrity check: PASSED")

    # First 16 bytes are the IV.
    iv = encrypted_data[:16]

    ciphertext = encrypted_data[16:]

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    decryptor = cipher.decryptor()

    padded_plaintext = (
        decryptor.update(ciphertext)
        + decryptor.finalize()
    )

    # Remove PKCS7 padding.
    unpadder = padding.PKCS7(128).unpadder()

    plaintext = (
        unpadder.update(padded_plaintext)
        + unpadder.finalize()
    )

    templates = pickle.loads(plaintext)

    return templates


def cosine_similarity(embedding1, embedding2):

    embedding1 = np.asarray(embedding1)
    embedding2 = np.asarray(embedding2)

    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(
        np.dot(embedding1, embedding2)
        / (norm1 * norm2)
    )


if __name__ == "__main__":

    print("======================================")
    print("AES BIOMETRIC SECURITY")
    print("======================================")

    encrypt_templates()

    templates = decrypt_templates()

    print("AES encrypted templates loaded successfully.")
    print("Registered subjects:", len(templates))

    print("======================================")
    print("AES SECURITY TEST PASSED")
    print("======================================")