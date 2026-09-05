import os
import shutil

from security import load_encrypted_templates


AES_FILE = r"models\face_templates_aes.enc"
BACKUP_FILE = r"models\face_templates_aes_test_backup.enc"


print("======================================")
print("BIOMETRIC TEMPLATE TAMPER TEST")
print("======================================")

# Create temporary backup
shutil.copy2(AES_FILE, BACKUP_FILE)

print("Temporary backup created.")

try:

    # Read original encrypted data
    with open(AES_FILE, "rb") as file:
        data = bytearray(file.read())

    # Modify one byte
    data[100] = data[100] ^ 1

    with open(AES_FILE, "wb") as file:
        file.write(data)

    print("Encrypted template modified.")
    print("Testing integrity verification...")
    print()

    try:

        load_encrypted_templates()

        print("ERROR: Tampering was NOT detected.")

    except ValueError as error:

        print("TAMPERING DETECTED SUCCESSFULLY.")
        print()
        print("Security message:")
        print(error)

finally:

    # Restore original encrypted template
    shutil.copy2(BACKUP_FILE, AES_FILE)

    # Remove temporary backup
    os.remove(BACKUP_FILE)

print()
print("Original AES template restored.")
print("======================================")
print("TAMPER TEST COMPLETED")
print("======================================")