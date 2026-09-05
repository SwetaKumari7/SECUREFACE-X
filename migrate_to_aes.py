import os
import pickle
import hashlib

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


DATA_DIR = r"data"
MODELS_DIR = r"models"

FERNET_KEY_FILE = os.path.join(DATA_DIR, "secret.key")
FERNET_TEMPLATE_FILE = os.path.join(MODELS_DIR, "face_templates.enc")

AES_KEY_FILE = os.path.join(DATA_DIR, "aes_secret.key")
AES_TEMPLATE_FILE = os.path.join(MODELS_DIR, "face_templates_aes.enc")
AES_HASH_FILE = os.path.join(MODELS_DIR, "face_templates_aes.sha256")


def decrypt_fernet_templates():

    print("Decrypting existing Fernet templates...")

    with open(FERNET_KEY_FILE, "rb") as file:
        key = file.read()

    with open(FERNET_TEMPLATE_FILE, "rb") as file:
        encrypted_data = file.read()

    cipher = Fernet(key)

    plaintext = cipher.decrypt(encrypted_data)

    templates = pickle.loads(plaintext)

    print("Fernet decryption: SUCCESS")
    print("Recovered subjects:", len(templates))

    return plaintext, templates


def get_or_create_aes_key():

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


def encrypt_with_aes(plaintext):

    print()
    print("Encrypting templates with AES-256...")

    key = get_or_create_aes_key()

    # AES uses a 16-byte IV.
    iv = os.urandom(16)

    # PKCS7 padding.
    padder = padding.PKCS7(128).padder()

    padded_data = (
        padder.update(plaintext)
        + padder.finalize()
    )

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    encryptor = cipher.encryptor()

    ciphertext = (
        encryptor.update(padded_data)
        + encryptor.finalize()
    )

    # Store IV + ciphertext.
    encrypted_data = iv + ciphertext

    with open(AES_TEMPLATE_FILE, "wb") as file:
        file.write(encrypted_data)

    # SHA-256 integrity hash.
    sha256_hash = hashlib.sha256(
        encrypted_data
    ).hexdigest()

    with open(AES_HASH_FILE, "w") as file:
        file.write(sha256_hash)

    print("AES-256 encryption: SUCCESS")
    print("AES file:", AES_TEMPLATE_FILE)
    print("SHA-256 file:", AES_HASH_FILE)

    return encrypted_data


def verify_aes_file():

    print()
    print("Verifying AES encrypted template...")

    key = get_or_create_aes_key()

    with open(AES_TEMPLATE_FILE, "rb") as file:
        encrypted_data = file.read()

    with open(AES_HASH_FILE, "r") as file:
        stored_hash = file.read().strip()

    current_hash = hashlib.sha256(
        encrypted_data
    ).hexdigest()

    if current_hash != stored_hash:
        raise ValueError(
            "SHA-256 integrity verification FAILED."
        )

    print("SHA-256 integrity check: PASSED")

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

    unpadder = padding.PKCS7(128).unpadder()

    plaintext = (
        unpadder.update(padded_plaintext)
        + unpadder.finalize()
    )

    templates = pickle.loads(plaintext)

    print("AES decryption test: PASSED")
    print("Recovered subjects:", len(templates))

    return templates


if __name__ == "__main__":

    print("======================================")
    print("FERNET → AES-256 MIGRATION")
    print("======================================")

    plaintext, original_templates = decrypt_fernet_templates()

    encrypt_with_aes(plaintext)

    recovered_templates = verify_aes_file()

    if len(original_templates) == len(recovered_templates):

        print()
        print("======================================")
        print("MIGRATION SUCCESSFUL")
        print("======================================")
        print("Original subjects:", len(original_templates))
        print("AES subjects:", len(recovered_templates))
        print()
        print("Existing Fernet file was NOT modified.")
        print("AES encryption is ready.")
        print("======================================")

    else:

        print()
        print("ERROR: Template count mismatch.")