import os
import shutil

from app import app


AES_FILE = r"models\face_templates_aes.enc"
BACKUP_FILE = r"models\face_templates_flask_test_backup.enc"


print("======================================")
print("FLASK BIOMETRIC SECURITY TEST")
print("======================================")

# Backup original template
shutil.copy2(
    AES_FILE,
    BACKUP_FILE
)

print("Original AES template backed up.")

try:

    # Modify one byte
    with open(
        AES_FILE,
        "rb"
    ) as file:

        data = bytearray(
            file.read()
        )

    data[100] = data[100] ^ 1

    with open(
        AES_FILE,
        "wb"
    ) as file:

        file.write(data)

    print("AES biometric template modified.")
    print()
    print("Starting Flask security check...")
    print()

    try:

        # Flask application startup performs
        # the blockchain/template integrity check.
        from blockchain import BiometricBlockchain

        blockchain = BiometricBlockchain()

        ok, message = (
            blockchain.verify_template_integrity(
                AES_FILE
            )
        )

        if not ok:

            print("======================================")
            print("ATTACK DETECTED")
            print("======================================")
            print(message)
            print()
            print("Authentication would be BLOCKED.")

        else:

            print(
                "ERROR: Tampering was not detected."
            )

    except Exception as error:

        print("SECURITY CHECK BLOCKED ACCESS.")
        print(error)

finally:

    # Restore original template
    shutil.copy2(
        BACKUP_FILE,
        AES_FILE
    )

    os.remove(
        BACKUP_FILE
    )

print()
print("Original AES template restored.")
print("======================================")
print("FLASK SECURITY TEST COMPLETED")
print("======================================")