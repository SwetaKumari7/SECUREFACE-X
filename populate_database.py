from database import get_connection, initialize_database
from security import load_encrypted_templates
from datetime import datetime


print("======================================")
print("POPULATING BIOMETRIC DATABASE")
print("======================================")


# Make sure database tables exist
initialize_database()


# Load encrypted biometric templates
templates = load_encrypted_templates()

print("Encrypted templates loaded.")
print("Registered subjects found:", len(templates))


connection = get_connection()
cursor = connection.cursor()


added = 0
existing = 0


for subject_id in templates.keys():

    subject_id = str(subject_id)

    # Check whether subject already exists
    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE subject_id = ?
        """,
        (subject_id,)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        existing += 1

    else:

        cursor.execute(
            """
            INSERT INTO users
            (
                subject_id,
                registration_date,
                status
            )
            VALUES (?, ?, ?)
            """,
            (
                subject_id,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "ACTIVE"
            )
        )

        added += 1


connection.commit()


# Count users
cursor.execute(
    "SELECT COUNT(*) AS total FROM users"
)

total_users = cursor.fetchone()["total"]


connection.close()


print()
print("Subjects added:", added)
print("Subjects already existing:", existing)
print("Total users in database:", total_users)

print()
print("======================================")
print("DATABASE POPULATION COMPLETED")
print("======================================")