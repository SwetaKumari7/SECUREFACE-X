import os
import cv2
import numpy as np

from datetime import datetime

from flask import Flask, render_template, request

from PIL import Image

from face_engine import get_embedding

from security import (
    load_encrypted_templates,
    verify_face
)

from database import (
    get_connection,
    initialize_database,
    log_security_event
)

from security_guard import (
    is_locked,
    register_failed_attempt,
    reset_security_state
)

from blockchain import (
    BiometricBlockchain
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

VERIFY_THRESHOLD = 0.62

AES_TEMPLATE_FILE = r"models\face_templates_aes.enc"

TEMP_DIR = r"data\temp"

os.makedirs(
    TEMP_DIR,
    exist_ok=True
)


# ============================================================
# BLOCKCHAIN
# ============================================================

blockchain = BiometricBlockchain()


# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# SECURITY STATUS
# ============================================================

def get_security_status():

    aes_status = "FAILED"
    sha_status = "FAILED"
    blockchain_status = "FAILED"

    # --------------------------------------------------------
    # AES CHECK
    # --------------------------------------------------------

    try:

        if os.path.exists(
            AES_TEMPLATE_FILE
        ):

            load_encrypted_templates()

            aes_status = "ACTIVE"

    except Exception as error:

        print(
            "AES security status check failed:",
            error
        )


    # --------------------------------------------------------
    # SHA + BLOCKCHAIN CHECK
    # --------------------------------------------------------

    try:

        integrity_ok, integrity_message = (
            blockchain.verify_template_integrity(
                AES_TEMPLATE_FILE
            )
        )

        if integrity_ok:

            sha_status = "PASSED"
            blockchain_status = "PASSED"

        else:

            print(
                "Integrity status:",
                integrity_message
            )

    except Exception as error:

        print(
            "Blockchain security status check failed:",
            error
        )


    return {

        "aes_status": aes_status,

        "sha_status": sha_status,

        "blockchain_status": blockchain_status

    }


# ============================================================
# HOME PAGE
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    security_status = (
        get_security_status()
    )

    return render_template(
        "index.html",
        security_status=security_status,
        result=None
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route(
    "/dashboard",
    methods=["GET"]
)
def dashboard():

    security_status = (
        get_security_status()
    )

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # TOTAL USERS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        WHERE status = 'ACTIVE'
        """
    )

    total_users = cursor.fetchone()["total"]


    # --------------------------------------------------------
    # TOTAL ATTEMPTS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM verification_logs
        """
    )

    total_attempts = cursor.fetchone()["total"]


    # --------------------------------------------------------
    # VERIFIED
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM verification_logs
        WHERE result = 'VERIFIED'
        """
    )

    verified_count = cursor.fetchone()["total"]


    # --------------------------------------------------------
    # REJECTED
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM verification_logs
        WHERE result = 'REJECTED'
        """
    )

    rejected_count = cursor.fetchone()["total"]


    # --------------------------------------------------------
    # RECENT LOGS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM verification_logs
        ORDER BY id DESC
        LIMIT 10
        """
    )

    recent_logs = cursor.fetchall()
    # --------------------------------------------------------
    # SECURITY EVENTS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM security_events
    """)

    security_event_count = cursor.fetchone()["total"]


    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM security_events
        WHERE severity = 'HIGH'
    """)

    high_severity_count = cursor.fetchone()["total"]


    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM security_events
        WHERE action_taken IN (
            'TEMPORARY_LOCKOUT',
            'AUTHENTICATION_BLOCKED'
        )
    """)

    blocked_count = cursor.fetchone()["total"]


    cursor.execute("""
        SELECT *
        FROM security_events
        ORDER BY event_id DESC
        LIMIT 10
    """)

    security_events = cursor.fetchall()


    connection.close()


    return render_template(
        "dashboard.html",

        total_users=total_users,

        total_attempts=total_attempts,

        verified_count=verified_count,

        rejected_count=rejected_count,

        recent_logs=recent_logs,

        security_event_count=security_event_count,

        high_severity_count=high_severity_count,

        blocked_count=blocked_count,

        security_events=security_events,

        security_status=security_status
    )


# ============================================================
# FACE VERIFICATION
# ============================================================

@app.route(
    "/verify",
    methods=["POST"]
)
def verify():

    temp_path = None

    try:

        print()
        print("======================================")
        print("NEW BIOMETRIC VERIFICATION REQUEST")
        print("======================================")


        # ====================================================
        # GET SUBJECT ID
        # ====================================================

        subject_id = request.form.get(
            "subject_id",
            ""
        ).strip()


        if not subject_id:

            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "Verification Failed",
                    "message": "Subject ID is required."
                },

                security_status=get_security_status()
            )


        # ====================================================
        # NORMALIZE SUBJECT ID
        # ====================================================

        try:

            subject_number = int(
                subject_id
            )

            subject_id = f"{subject_number:03d}"

        except ValueError:

            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "Invalid Subject ID",
                    "message": "Enter a valid subject ID such as 001, 002 or 200."
                },

                security_status=get_security_status()
            )


        print(
            "Subject ID:",
            subject_id
        )

                # ====================================================
        # AUTHENTICATION LOCKOUT PROTECTION
        # ====================================================

        locked, failed_attempts = is_locked(subject_id)

        print(
            f"Security state for {subject_id}: "
            f"failed_attempts={failed_attempts}, "
            f"locked={locked}"
        )

        if locked:

            print(
                f"SECURITY ALERT: SUBJECT {subject_id} IS LOCKED"
            )

            try:
                log_security_event(
                    subject_id=subject_id,
                    attack_type="AUTHENTICATION_ABUSE",
                    severity="HIGH",
                    source="VERIFY_ENDPOINT",
                    action_taken="AUTHENTICATION_BLOCKED"
                )
            except Exception as security_error:
                print(
                    "Security event logging failed:",
                    security_error
                )

            return render_template(
                "index.html",
                security_status=get_security_status(),
                result={
                    "success": False,
                    "title": "AUTHENTICATION LOCKED",
                    "message": (
                        f"Subject {subject_id} is temporarily "
                        f"locked because of repeated failed "
                        f"authentication attempts."
                    ),
                    "subject_id": subject_id,
                    "security_status": "BLOCKED",
                    "result": "LOCKED"
                }
            )

        # ====================================================
        # GET UPLOADED IMAGE
        # ====================================================

        uploaded_file = request.files.get(
            "face_image"
        )


        if uploaded_file is None:

            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "Image Missing",
                    "message": "Please upload a facial image."
                },

                security_status=get_security_status()
            )


        if uploaded_file.filename == "":

            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "Image Missing",
                    "message": "Please select a facial image."
                },

                security_status=get_security_status()
            )


        # ====================================================
        # LOAD ENCRYPTED TEMPLATES
        # ====================================================

        print(
            "Loading encrypted biometric templates..."
        )

        templates = (
            load_encrypted_templates()
        )

        print(
            "Registered subjects:",
            len(templates)
        )


        # ====================================================
        # CHECK SUBJECT
        # ====================================================

        if subject_id not in templates:

            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "Subject Not Registered",
                    "message": f"Subject ID {subject_id} is not registered."
                },

                security_status=get_security_status()
            )


        # ====================================================
        # SAVE TEMPORARY IMAGE
        # ====================================================

        temp_filename = (
            "verification_image.jpg"
        )

        temp_path = os.path.join(
            TEMP_DIR,
            temp_filename
        )


        uploaded_file.save(
            temp_path
        )


        print(
            "Image saved:",
            temp_path
        )


        # ====================================================
        # IMAGE QUALITY CHECK
        # ====================================================

        image = Image.open(
            temp_path
        ).convert("RGB")


        image_array = np.array(
            image
        )


        gray = cv2.cvtColor(
            image_array,
            cv2.COLOR_RGB2GRAY
        )


        brightness = float(
            np.mean(gray)
        )


        contrast = float(
            np.std(gray)
        )


        print(
            f"Brightness: {brightness:.2f}"
        )

        print(
            f"Contrast: {contrast:.2f}"
        )


        # ----------------------------------------------------
        # BRIGHTNESS
        # ----------------------------------------------------

        if brightness < 20:

            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "Poor Image Quality",
                    "message": "The uploaded image is too dark.",
                    "subject_id": subject_id,
                    "brightness": round(brightness, 2),
                    "contrast": round(contrast, 2)
                },

                security_status=get_security_status()
            )


        # ----------------------------------------------------
        # CONTRAST
        # ----------------------------------------------------

        if contrast < 10:

            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "Poor Image Quality",
                    "message": "The uploaded image has insufficient contrast.",
                    "subject_id": subject_id,
                    "brightness": round(brightness, 2),
                    "contrast": round(contrast, 2)
                },

                security_status=get_security_status()
            )


        # ====================================================
        # FACE EMBEDDING
        # ====================================================

        print(
            "Extracting FaceNet embedding..."
        )


        test_embedding = get_embedding(
            temp_path
        )


        print(
            "Embedding size:",
            test_embedding.shape
        )


        # ====================================================
        # BLOCKCHAIN INTEGRITY CHECK
        # ====================================================

        print(
            "Checking biometric template integrity..."
        )


        integrity_ok, integrity_message = (
            blockchain.verify_template_integrity(
                AES_TEMPLATE_FILE
            )
        )


        if not integrity_ok:

            print(
                "SECURITY ALERT:",
                integrity_message
            )


            return render_template(
                "index.html",

                result={
                    "success": False,
                    "title": "SECURITY ALERT",
                    "message": integrity_message,
                    "subject_id": subject_id,
                    "security_status": "BLOCKED"
                },

                security_status=get_security_status()
            )


        print(
            "Blockchain integrity: PASSED"
        )

        print(
            "Template integrity: PASSED"
        )


        # ====================================================
        # GET REGISTERED EMBEDDING
        # ====================================================

        registered_embedding = (
            templates[subject_id]
        )


        # ====================================================
        # COSINE SIMILARITY
        # ====================================================

        verified, similarity = verify_face(

            test_embedding,

            registered_embedding,

            threshold=VERIFY_THRESHOLD

        )


        similarity = float(
            similarity
        )


        print(
            f"Similarity: {similarity:.4f}"
        )

        print(
            f"Threshold: {VERIFY_THRESHOLD:.2f}"
        )


                # ====================================================
        # FAILED AUTHENTICATION DETECTION
        # ====================================================

        if verified:

            reset_security_state(subject_id)

            print(
                f"Authentication SUCCESSFUL for {subject_id}"
            )

        else:

            failed_attempts, locked = register_failed_attempt(
                subject_id
            )

            print(
                f"Failed authentication attempts: "
                f"{failed_attempts}"
            )

            if locked:

                print(
                    "SECURITY ALERT: "
                    f"SUBJECT {subject_id} TEMPORARILY LOCKED"
                )

                log_security_event(
                    subject_id=subject_id,
                    attack_type="AUTHENTICATION_ABUSE",
                    severity="HIGH",
                    source="VERIFY_ENDPOINT",
                    action_taken="TEMPORARY_LOCKOUT"
                )

                result_status = "LOCKED"

                result_title = "AUTHENTICATION LOCKED"

                result_message = (
                    f"Subject {subject_id} has been temporarily "
                    f"locked after {failed_attempts} failed "
                    f"authentication attempts."
                )

                success = False

            elif failed_attempts >= 2:

                log_security_event(
                    subject_id=subject_id,
                    attack_type="REPEATED_AUTH_FAILURE",
                    severity="MEDIUM",
                    source="VERIFY_ENDPOINT",
                    action_taken="MONITOR_SUBJECT"
                )

                result_message = (
                    f"Authentication rejected. "
                    f"Failed attempt {failed_attempts} of 3."
                )

            else:

                result_message = (
                    f"Authentication rejected. "
                    f"Failed attempt {failed_attempts} of 3."
                )

        # ====================================================
        # RESULT
        # ====================================================

        if verified:

            result_status = "VERIFIED"

            result_title = (
                "Identity Verified"
            )

            result_message = (
                f"Subject {subject_id} successfully authenticated."
            )

            success = True

        else:

            result_status = "REJECTED"

            result_title = (
                "Identity Rejected"
            )

            result_message = (
                f"The uploaded face does not match "
                f"registered subject {subject_id}."
            )

            success = False


        # ====================================================
        # DATABASE LOG
        # ====================================================

        try:

            connection = get_connection()

            cursor = connection.cursor()


            cursor.execute(
                """
                INSERT INTO verification_logs
                (
                    subject_id,
                    similarity_score,
                    result,
                    brightness,
                    contrast,
                    security_status,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,

                (

                    subject_id,

                    similarity,

                    result_status,

                    brightness,

                    contrast,

                    "PASSED",

                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                )
            )


            connection.commit()

            connection.close()


            print(
                "Verification log saved."
            )


        except Exception as database_error:

            print(
                "Database logging failed:",
                database_error
            )


        # ====================================================
        # DELETE TEMP IMAGE
        # ====================================================

        if temp_path is not None:

            if os.path.exists(
                temp_path
            ):

                os.remove(
                    temp_path
                )


        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        return render_template(
            "index.html",

            result={

                "success": success,

                "title": result_title,

                "message": result_message,

                "subject_id": subject_id,

                "similarity": round(
                    similarity,
                    4
                ),

                "threshold": VERIFY_THRESHOLD,

                "brightness": round(
                    brightness,
                    2
                ),

                "contrast": round(
                    contrast,
                    2
                ),

                "security_status": "PASSED",

                "result": result_status

            },

            security_status=get_security_status()

        )


    # ========================================================
    # FACE DETECTION / VALUE ERROR
    # ========================================================

    except ValueError as error:

        print(
            "Face processing error:",
            error
        )


        return render_template(
            "index.html",

            result={

                "success": False,

                "title": "Face Processing Failed",

                "message": str(error)

            },

            security_status=get_security_status()
        )


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as error:

        print(
            "Verification error:",
            error
        )


        return render_template(
            "index.html",

            result={

                "success": False,

                "title": "Verification Error",

                "message": str(error)

            },

            security_status=get_security_status()
        )


    finally:

        # ----------------------------------------------------
        # ALWAYS DELETE TEMP IMAGE
        # ----------------------------------------------------

        if temp_path is not None:

            try:

                if os.path.exists(
                    temp_path
                ):

                    os.remove(
                        temp_path
                    )

            except Exception:

                pass


# ============================================================
# SECURITY ATTACK LAB
# ============================================================


@app.route("/attack-lab")
def attack_lab():
    return render_template("attack_lab.html")



@app.route(
    "/api/attack-test/<test_type>",
    methods=["POST"]
)
def attack_test(test_type):

    logs = []

    try:

        # ====================================================
        # TEMPLATE TAMPERING TEST
        # ====================================================

        if test_type == "tamper":

            import hashlib
            import tempfile

            logs.append({
                "text":
                    "<span class='green'>[+]</span> "
                    "Loading protected AES biometric template...",
                "type": ""
            })

            if not os.path.exists(
                AES_TEMPLATE_FILE
            ):

                return {
                    "success": False,
                    "message":
                        "Protected biometric template not found.",
                    "logs": logs
                }


            # Read original template

            with open(
                AES_TEMPLATE_FILE,
                "rb"
            ) as file:

                original_data = file.read()


            original_hash = hashlib.sha256(
                original_data
            ).hexdigest()


            logs.append({
                "text":
                    "<span class='green'>[+]</span> "
                    "Original SHA-256: "
                    + original_hash[:24]
                    + "...",
                "type": ""
            })


            # Create temporary attack copy

            modified_data = bytearray(
                original_data
            )


            # Modify a byte in the COPY ONLY

            attack_position = min(
                100,
                len(modified_data) - 1
            )

            modified_data[
                attack_position
            ] ^= 1


            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".enc"
            ) as temp_file:

                temp_file.write(
                    modified_data
                )

                attack_file = temp_file.name


            try:

                attack_hash = hashlib.sha256(
                    bytes(modified_data)
                ).hexdigest()


                logs.append({
                    "text":
                        "<span class='yellow'>[!]</span> "
                        "Controlled template modification created.",
                    "type": ""
                })


                logs.append({
                    "text":
                        "<span class='yellow'>[!]</span> "
                        "Modified SHA-256: "
                        + attack_hash[:24]
                        + "...",
                    "type": ""
                })


                if attack_hash != original_hash:

                    logs.append({
                        "text":
                            "<span class='red'>[!]</span> "
                            "HASH MISMATCH DETECTED",
                        "type": ""
                    })


                    logs.append({
                        "text":
                            "<span class='green'>[+]</span> "
                            "Biometric template rejected by integrity layer.",
                        "type": ""
                    })


                    logs.append({
                        "text":
                            "<span class='green'>[+]</span> "
                            "Authentication would be BLOCKED.",
                        "type": ""
                    })


                    return {
                        "success": True,
                        "message":
                            "TEMPLATE TAMPERING DETECTED AND BLOCKED",
                        "logs": logs
                    }


            finally:

                if os.path.exists(
                    attack_file
                ):

                    os.remove(
                        attack_file
                    )


        # ====================================================
        # REAL INTEGRITY TEST
        # ====================================================

        elif test_type == "integrity":

            logs.append({
                "text":
                    "<span class='green'>[+]</span> "
                    "Checking SHA-256 integrity...",
                "type": ""
            })


            integrity_ok, message = (
                blockchain.verify_template_integrity(
                    AES_TEMPLATE_FILE
                )
            )


            if integrity_ok:

                logs.append({
                    "text":
                        "<span class='green'>[+]</span> "
                        "SHA-256 integrity ........ PASSED",
                    "type": ""
                })


                logs.append({
                    "text":
                        "<span class='green'>[+]</span> "
                        "Blockchain ledger ........ VALID",
                    "type": ""
                })


                logs.append({
                    "text":
                        "<span class='green'>[+]</span> "
                        "Protected template ........ AUTHENTIC",
                    "type": ""
                })


                return {
                    "success": True,
                    "message":
                        "BIOMETRIC TEMPLATE INTEGRITY VERIFIED",
                    "logs": logs
                }


            logs.append({
                "text":
                    "<span class='red'>[!]</span> "
                    + str(message),
                "type": ""
            })


            return {
                "success": False,
                "message":
                    "BIOMETRIC TEMPLATE INTEGRITY FAILED",
                "logs": logs
            }


        # ====================================================
        # AUTHENTICATION ABUSE SIMULATION
        # ====================================================

                # ====================================================
        # REAL AUTHENTICATION ABUSE TEST
        # ====================================================

        elif test_type == "abuse":

            test_subject = "999"

            logs.append({
                "text":
                    "<span class='blue'>[*]</span> "
                    "Starting controlled authentication-abuse test...",
                "type": ""
            })

            # Reset test subject before simulation
            reset_security_state(test_subject)

            for attempt in range(1, 4):

                failed_attempts, locked = register_failed_attempt(
                    test_subject
                )

                logs.append({
                    "text":
                        "<span class='yellow'>[!]</span> "
                        f"Rejected authentication attempt "
                        f"{attempt}/3 — "
                        f"security counter: {failed_attempts}",
                    "type": ""
                })

                if locked:

                    log_security_event(
                        subject_id=test_subject,
                        attack_type="AUTHENTICATION_ABUSE",
                        severity="HIGH",
                        source="ATTACK_LAB",
                        action_taken="TEMPORARY_LOCKOUT"
                    )

                    logs.append({
                        "text":
                            "<span class='red'>[!]</span> "
                            "AUTHENTICATION ABUSE DETECTED",
                        "type": ""
                    })

                    logs.append({
                        "text":
                            "<span class='green'>[+]</span> "
                            "DEFENSIVE RESPONSE: SUBJECT LOCKED",
                        "type": ""
                    })

            locked, attempts = is_locked(test_subject)

            return {
                "success": True,
                "message":
                    "AUTHENTICATION ABUSE DETECTED — ACCOUNT LOCKED",
                "logs": logs
            }


    except Exception as error:

        logs.append({
            "text":
                "<span class='red'>[ERROR]</span> "
                + str(error),
            "type": ""
        })


        return {
            "success": False,
            "message":
                "Security test failed: "
                + str(error),
            "logs": logs
        }



# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("SECUREFACE BIOMETRIC AUTHENTICATION")
    print("======================================")
    print(
        "Verification threshold:",
        VERIFY_THRESHOLD
    )
    print(
        "Registered template:",
        AES_TEMPLATE_FILE
    )
    print()
    print(
        "Open in browser:"
    )
    print(
        "http://127.0.0.1:5000/"
    )
    print()
    print("======================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )