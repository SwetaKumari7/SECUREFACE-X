import os
import uuid
import cv2
import numpy as np

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from face_engine import get_embedding
from security import load_encrypted_templates, verify_face
from blockchain import BiometricBlockchain


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}


AES_TEMPLATE_FILE = r"models\face_templates_aes.enc"

BRIGHTNESS_THRESHOLD = 20
CONTRAST_THRESHOLD = 10

VERIFICATION_THRESHOLD = 0.62


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


# -----------------------------------------
# LOAD ENCRYPTED BIOMETRIC TEMPLATES
# -----------------------------------------

templates = load_encrypted_templates()


# -----------------------------------------
# BLOCKCHAIN INTEGRITY CHECK
# -----------------------------------------

blockchain = BiometricBlockchain()

blockchain_ok, blockchain_message = (
    blockchain.verify_template_integrity(
        AES_TEMPLATE_FILE
    )
)

if not blockchain_ok:

    raise RuntimeError(
        "BIOMETRIC SECURITY CHECK FAILED: "
        + blockchain_message
    )

print("Blockchain integrity: PASSED")
print("Template integrity: PASSED")


# -----------------------------------------
# IMAGE QUALITY CHECK
# -----------------------------------------

def check_image_quality(image_path):

    image = cv2.imread(image_path)

    if image is None:

        return False, 0.0, 0.0

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(
        np.mean(gray)
    )

    contrast = float(
        np.std(gray)
    )

    quality_ok = (
        brightness >= BRIGHTNESS_THRESHOLD
        and
        contrast >= CONTRAST_THRESHOLD
    )

    return (
        quality_ok,
        brightness,
        contrast
    )


# -----------------------------------------
# MAIN ROUTE
# -----------------------------------------

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    result = None
    similarity = None
    message = None

    brightness = None
    contrast = None

    if request.method == "POST":

        subject_id = request.form.get(
            "subject_id",
            ""
        ).strip()

        face_file = request.files.get(
            "face_image"
        )

        # ---------------------------------
        # SUBJECT ID CHECK
        # ---------------------------------

        if not subject_id:

            message = (
                "Please enter a subject ID."
            )

            return render_template(
                "index.html",
                result=result,
                similarity=similarity,
                message=message
            )

        if subject_id not in templates:

            message = (
                f"Subject ID {subject_id} "
                "is not registered."
            )

            return render_template(
                "index.html",
                result=result,
                similarity=similarity,
                message=message
            )

        # ---------------------------------
        # FILE CHECK
        # ---------------------------------

        if (
            face_file is None
            or face_file.filename == ""
        ):

            message = (
                "Please select a face image."
            )

            return render_template(
                "index.html",
                result=result,
                similarity=similarity,
                message=message
            )

        if not allowed_file(
            face_file.filename
        ):

            message = (
                "Invalid file type. "
                "Please upload JPG, JPEG, or PNG."
            )

            return render_template(
                "index.html",
                result=result,
                similarity=similarity,
                message=message
            )

        # ---------------------------------
        # TEMPORARY FILE
        # ---------------------------------

        original_filename = secure_filename(
            face_file.filename
        )

        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()

        filename = (
            f"{uuid.uuid4().hex}.{extension}"
        )

        image_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        face_file.save(
            image_path
        )

        try:

            # -----------------------------
            # IMAGE QUALITY
            # -----------------------------

            (
                quality_ok,
                brightness,
                contrast
            ) = check_image_quality(
                image_path
            )

            if not quality_ok:

                message = (
                    "Image quality is too low. "
                    "Please upload a clearer and "
                    "better-lit face image."
                )

                return render_template(
                    "index.html",
                    result=result,
                    similarity=similarity,
                    message=message,
                    brightness=round(
                        brightness,
                        2
                    ),
                    contrast=round(
                        contrast,
                        2
                    )
                )

            # -----------------------------
            # FACE EMBEDDING
            # -----------------------------

            try:

                embedding = get_embedding(
                    image_path
                )

            except Exception as error:

                message = (
                    f"Face processing failed: "
                    f"{error}"
                )

                return render_template(
                    "index.html",
                    result=result,
                    similarity=similarity,
                    message=message,
                    brightness=round(
                        brightness,
                        2
                    ),
                    contrast=round(
                        contrast,
                        2
                    )
                )

            # -----------------------------
            # FINAL SECURITY CHECK
            # -----------------------------

            blockchain_ok, blockchain_message = (
                blockchain.verify_template_integrity(
                    AES_TEMPLATE_FILE
                )
            )

            if not blockchain_ok:

                result = "SECURITY ALERT"

                message = (
                    "Biometric template integrity "
                    "verification failed. "
                    "Authentication stopped."
                )

                print(
                    "SECURITY ALERT:",
                    blockchain_message
                )

                return render_template(
                    "index.html",
                    result=result,
                    similarity=None,
                    message=message,
                    brightness=round(
                        brightness,
                        2
                    ),
                    contrast=round(
                        contrast,
                        2
                    )
                )

            # -----------------------------
            # BIOMETRIC VERIFICATION
            # -----------------------------

            registered_embedding = (
                templates[subject_id]
            )

            verified, score = verify_face(
                embedding,
                registered_embedding,
                threshold=VERIFICATION_THRESHOLD
            )

            similarity = round(
                score,
                4
            )

            result = (
                "VERIFIED"
                if verified
                else "REJECTED"
            )

        finally:

            # -----------------------------
            # DELETE TEMPORARY IMAGE
            # -----------------------------

            try:

                if os.path.exists(
                    image_path
                ):

                    os.remove(
                        image_path
                    )

            except OSError:

                pass

    return render_template(
        "index.html",
        result=result,
        similarity=similarity,
        message=message,
        brightness=brightness,
        contrast=contrast
    )


if __name__ == "__main__":

    print("======================================")
    print("SECURE FACE AUTHENTICATION")
    print("======================================")
    print(
        "Registered subjects:",
        len(templates)
    )
    print(
        "Verification threshold:",
        VERIFICATION_THRESHOLD
    )
    print(
        "Encryption: AES-256-CBC"
    )
    print(
        "Integrity: SHA-256"
    )
    print(
        "Blockchain integrity: ENABLED"
    )
    print(
        "Allowed files: JPG, JPEG, PNG"
    )
    print(
        "Temporary uploads are deleted"
    )
    print("Starting Flask server...")
    print("======================================")

    app.run(
        debug=True
    )