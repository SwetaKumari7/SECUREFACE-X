import os
import pickle
import hashlib
import numpy as np

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


DATA_DIR = r"data"
MODELS_DIR = r"models"

AES_KEY_FILE = os.path.join(DATA_DIR, "aes_secret.key")
AES_TEMPLATE_FILE = os.path.join(
    MODELS_DIR,
    "face_templates_aes.enc"
)
AES_HASH_FILE = os.path.join(
    MODELS_DIR,
    "face_templates_aes.sha256"
)


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def get_aes_key():

    if not os.path.exists(AES_KEY_FILE):
        raise FileNotFoundError(
            "AES key was not found."
        )

    with open(AES_KEY_FILE, "rb") as file:
        key = file.read()

    if len(key) != 32:
        raise ValueError(
            "Invalid AES key. AES-256 requires 32 bytes."
        )

    return key


def verify_integrity(encrypted_data):

    if not os.path.exists(AES_HASH_FILE):
        raise FileNotFoundError(
            "SHA-256 integrity file was not found."
        )

    with open(AES_HASH_FILE, "r") as file:
        stored_hash = file.read().strip()

    current_hash = hashlib.sha256(
        encrypted_data
    ).hexdigest()

    if current_hash != stored_hash:
        raise ValueError(
            "INTEGRITY CHECK FAILED: "
            "Encrypted biometric template has been modified."
        )

    return True


def load_encrypted_templates():

    if not os.path.exists(AES_TEMPLATE_FILE):
        raise FileNotFoundError(
            "AES encrypted biometric templates were not found."
        )

    key = get_aes_key()

    with open(AES_TEMPLATE_FILE, "rb") as file:
        encrypted_data = file.read()

    # -----------------------------------------
    # SHA-256 INTEGRITY VERIFICATION
    # -----------------------------------------

    verify_integrity(encrypted_data)

    print("SHA-256 integrity check: PASSED")

    # -----------------------------------------
    # Extract IV and ciphertext
    # -----------------------------------------

    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # -----------------------------------------
    # AES-256-CBC DECRYPTION
    # -----------------------------------------

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    decryptor = cipher.decryptor()

    padded_plaintext = (
        decryptor.update(ciphertext)
        + decryptor.finalize()
    )

    # -----------------------------------------
    # Remove PKCS7 padding
    # -----------------------------------------

    unpadder = padding.PKCS7(128).unpadder()

    plaintext = (
        unpadder.update(padded_plaintext)
        + unpadder.finalize()
    )

    # -----------------------------------------
    # Restore biometric templates
    # -----------------------------------------

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


def verify_face(
    test_embedding,
    registered_embedding,
    threshold=0.62
):

    similarity = cosine_similarity(
        test_embedding,
        registered_embedding
    )

    verified = similarity >= threshold

    return verified, similarity


if __name__ == "__main__":

    print("======================================")
    print("AES BIOMETRIC SECURITY")
    print("======================================")

    templates = load_encrypted_templates()

    print("AES-256 encrypted templates loaded.")
    print("Registered subjects:", len(templates))
    print("Encryption: AES-256-CBC")
    print("Integrity: SHA-256")
    print("Verification threshold: 0.62")

    print("======================================")
    print("SECURITY TEST PASSED")
    print("======================================")