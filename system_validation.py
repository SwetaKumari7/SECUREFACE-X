import os
import sqlite3
import json


print("==============================================")
print("       SECUREFACE SYSTEM VALIDATION")
print("==============================================")
print()


errors = []
passed = []


def check_file(path, name):

    if os.path.exists(path):

        passed.append(name)

        print(
            f"[PASS] {name}"
        )

        return True

    else:

        errors.append(name)

        print(
            f"[FAIL] {name}"
        )

        return False


# ------------------------------------------------
# CORE FILES
# ------------------------------------------------

print("CORE FILES")
print("----------------------------------------------")

check_file(
    "app.py",
    "Flask application"
)

check_file(
    "face_engine.py",
    "Face engine"
)

check_file(
    "security.py",
    "Security module"
)

check_file(
    "blockchain.py",
    "Blockchain module"
)

check_file(
    "database.py",
    "Database module"
)


print()


# ------------------------------------------------
# MODEL FILES
# ------------------------------------------------

print("BIOMETRIC TEMPLATES")
print("----------------------------------------------")

check_file(
    r"models\face_templates_aes.enc",
    "AES encrypted templates"
)

check_file(
    r"models\face_templates_aes.sha256",
    "SHA-256 integrity file"
)

check_file(
    r"data\aes_secret.key",
    "AES-256 secret key"
)


print()


# ------------------------------------------------
# BLOCKCHAIN
# ------------------------------------------------

print("BLOCKCHAIN")
print("----------------------------------------------")

blockchain_file = (
    r"models\biometric_blockchain.json"
)

if os.path.exists(blockchain_file):

    try:

        with open(
            blockchain_file,
            "r",
            encoding="utf-8"
        ) as file:

            blockchain = json.load(file)

        if len(blockchain) >= 2:

            passed.append(
                "Blockchain ledger"
            )

            print(
                "[PASS] Blockchain ledger"
            )

        else:

            errors.append(
                "Blockchain ledger has insufficient blocks"
            )

            print(
                "[FAIL] Blockchain ledger"
            )

    except Exception as error:

        errors.append(
            f"Blockchain error: {error}"
        )

        print(
            "[FAIL] Blockchain validation"
        )

else:

    errors.append(
        "Blockchain ledger file"
    )

    print(
        "[FAIL] Blockchain ledger"
    )


print()


# ------------------------------------------------
# DATABASE
# ------------------------------------------------

print("DATABASE")
print("----------------------------------------------")


database_file = "biomatch.db"


if os.path.exists(database_file):

    try:

        connection = sqlite3.connect(
            database_file
        )

        cursor = connection.cursor()


        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )

        users = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(*) FROM verification_logs"
        )

        logs = cursor.fetchone()[0]


        connection.close()


        print(
            "[PASS] SQLite database"
        )

        print(
            f"[INFO] Registered users: {users}"
        )

        print(
            f"[INFO] Verification logs: {logs}"
        )


        if users == 200:

            passed.append(
                "200 registered subjects"
            )

            print(
                "[PASS] 200 registered subjects"
            )

        else:

            errors.append(
                f"Expected 200 users, found {users}"
            )

    except Exception as error:

        errors.append(
            f"Database error: {error}"
        )

        print(
            "[FAIL] Database validation"
        )

else:

    errors.append(
        "SQLite database"
    )

    print(
        "[FAIL] SQLite database"
    )


print()


# ------------------------------------------------
# TEMPLATES
# ------------------------------------------------

print("WEB INTERFACE")
print("----------------------------------------------")

check_file(
    r"templates\index.html",
    "Verification interface"
)

check_file(
    r"templates\dashboard.html",
    "Security dashboard"
)


print()


# ------------------------------------------------
# FINAL RESULT
# ------------------------------------------------

print("==============================================")
print("FINAL VALIDATION")
print("==============================================")


print(
    "Passed checks:",
    len(passed)
)

print(
    "Failed checks:",
    len(errors)
)

print()


if len(errors) == 0:

    print(
        "SYSTEM STATUS: READY FOR DEMONSTRATION"
    )

else:

    print(
        "SYSTEM STATUS: REVIEW REQUIRED"
    )

    print()

    print(
        "Problems:"
    )

    for error in errors:

        print(
            "-",
            error
        )


print(
    "=============================================="
)