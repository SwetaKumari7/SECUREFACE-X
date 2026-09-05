import os
import json
import shutil

from blockchain import BiometricBlockchain


BLOCKCHAIN_FILE = r"models\biometric_blockchain.json"
BACKUP_FILE = r"models\biometric_blockchain_test_backup.json"


print("======================================")
print("BLOCKCHAIN TAMPER TEST")
print("======================================")

# Create temporary backup
shutil.copy2(BLOCKCHAIN_FILE, BACKUP_FILE)

print("Temporary blockchain backup created.")

try:

    # Load blockchain JSON
    with open(
        BLOCKCHAIN_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        blockchain_data = json.load(file)

    # Modify one value inside Block 1
    blockchain_data[1]["template_hash"] = (
        "TAMPERED_HASH_VALUE"
    )

    # Save modified blockchain
    with open(
        BLOCKCHAIN_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            blockchain_data,
            file,
            indent=4
        )

    print("Blockchain record modified.")
    print("Testing blockchain integrity...")
    print()

    blockchain = BiometricBlockchain()

    if blockchain.verify_chain():

        print("ERROR: Blockchain tampering was NOT detected.")

    else:

        print("BLOCKCHAIN TAMPERING DETECTED SUCCESSFULLY.")

except Exception as error:

    print("Security test error:")
    print(error)

finally:

    # Restore original blockchain
    shutil.copy2(
        BACKUP_FILE,
        BLOCKCHAIN_FILE
    )

    os.remove(BACKUP_FILE)

print()
print("Original blockchain restored.")
print("======================================")
print("BLOCKCHAIN TAMPER TEST COMPLETED")
print("======================================")