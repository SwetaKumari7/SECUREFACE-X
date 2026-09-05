import os
import csv
import cv2
import numpy as np

from face_engine import get_embedding
from security import load_encrypted_templates


# ============================================================
# CONFIGURATION
# ============================================================

TEST_DIR = r"dataset\FEI_DATABASE\TESTING"

OUTPUT_FILE = "quality_filtered_results.csv"

BRIGHTNESS_THRESHOLD = 20
CONTRAST_THRESHOLD = 10

BIOMETRIC_THRESHOLDS = np.arange(
    0.30,
    0.96,
    0.01
)


# ============================================================
# IMAGE QUALITY FUNCTION
# ============================================================

def check_image_quality(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return False, 0.0, 0.0, 0.0

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(np.mean(gray))

    contrast = float(np.std(gray))

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    edge_ratio = float(
        np.mean(edges > 0)
    ) * 100

    quality_ok = (
        brightness >= BRIGHTNESS_THRESHOLD
        and
        contrast >= CONTRAST_THRESHOLD
    )

    return (
        quality_ok,
        brightness,
        contrast,
        edge_ratio
    )


# ============================================================
# START
# ============================================================

print("======================================")
print("QUALITY-FILTERED VERIFICATION")
print("======================================")
print()

print(
    "Brightness threshold:",
    BRIGHTNESS_THRESHOLD
)

print(
    "Contrast threshold:",
    CONTRAST_THRESHOLD
)

print()


# ============================================================
# LOAD ENCRYPTED TEMPLATES
# ============================================================

print("Loading encrypted biometric templates...")

templates = load_encrypted_templates()

print(
    "Registered subjects:",
    len(templates)
)

print()


# ============================================================
# STORAGE
# ============================================================

genuine_scores = []
impostor_scores = []

total_images = 0
quality_passed = 0
quality_rejected = 0
face_detection_failed = 0


# ============================================================
# GET SUBJECTS
# ============================================================

subjects = sorted(
    [
        folder
        for folder in os.listdir(TEST_DIR)
        if os.path.isdir(
            os.path.join(TEST_DIR, folder)
        )
    ]
)


# ============================================================
# PROCESS TESTING DATA
# ============================================================

for subject_index, subject in enumerate(
    subjects,
    start=1
):

    subject_path = os.path.join(
        TEST_DIR,
        subject
    )

    image_files = sorted(
        [
            file
            for file in os.listdir(subject_path)
            if file.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png"
                )
            )
        ]
    )

    for image_file in image_files:

        total_images += 1

        image_path = os.path.join(
            subject_path,
            image_file
        )

        # ----------------------------------------------------
        # IMAGE QUALITY CHECK
        # ----------------------------------------------------

        (
            quality_ok,
            brightness,
            contrast,
            edge_ratio
        ) = check_image_quality(
            image_path
        )

        if not quality_ok:

            quality_rejected += 1

            continue

        quality_passed += 1


        # ----------------------------------------------------
        # FACE EMBEDDING
        # ----------------------------------------------------

        try:

            embedding = get_embedding(
                image_path
            )

        except Exception as error:

            face_detection_failed += 1

            print(
                f"Embedding failed: "
                f"{subject}/{image_file}"
            )

            print(
                f"Reason: {error}"
            )

            continue


        # ----------------------------------------------------
        # NORMALIZE EMBEDDING
        # ----------------------------------------------------

        embedding = np.asarray(
            embedding,
            dtype=np.float32
        )

        embedding_norm = np.linalg.norm(
            embedding
        )

        if embedding_norm == 0:

            face_detection_failed += 1

            print(
                f"Invalid embedding: "
                f"{subject}/{image_file}"
            )

            continue

        embedding = (
            embedding /
            embedding_norm
        )


        # ----------------------------------------------------
        # GENUINE SCORE
        # ----------------------------------------------------

        if subject not in templates:

            print(
                f"Warning: template not found "
                f"for subject {subject}"
            )

            continue

        genuine_template = np.asarray(
            templates[subject],
            dtype=np.float32
        )

        genuine_template_norm = np.linalg.norm(
            genuine_template
        )

        if genuine_template_norm == 0:

            print(
                f"Warning: invalid template "
                f"for subject {subject}"
            )

            continue

        genuine_template = (
            genuine_template /
            genuine_template_norm
        )

        genuine_score = float(
            np.dot(
                embedding,
                genuine_template
            )
        )

        genuine_scores.append(
            genuine_score
        )


        # ----------------------------------------------------
        # IMPOSTOR SCORES
        # ----------------------------------------------------

        for (
            other_subject,
            other_template
        ) in templates.items():

            if other_subject == subject:
                continue

            other_template = np.asarray(
                other_template,
                dtype=np.float32
            )

            other_norm = np.linalg.norm(
                other_template
            )

            if other_norm == 0:
                continue

            other_template = (
                other_template /
                other_norm
            )

            impostor_score = float(
                np.dot(
                    embedding,
                    other_template
                )
            )

            impostor_scores.append(
                impostor_score
            )


    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if subject_index % 10 == 0:

        print(
            f"Progress: "
            f"{subject_index}/{len(subjects)} subjects"
        )


# ============================================================
# CONVERT TO NUMPY
# ============================================================

genuine_scores = np.array(
    genuine_scores,
    dtype=np.float32
)

impostor_scores = np.array(
    impostor_scores,
    dtype=np.float32
)


# ============================================================
# SUMMARY
# ============================================================

print()

print("======================================")
print("QUALITY FILTER SUMMARY")
print("======================================")
print()

print(
    "Total images:",
    total_images
)

print(
    "Quality passed:",
    quality_passed
)

print(
    "Quality rejected:",
    quality_rejected
)

print(
    "Face detection failures:",
    face_detection_failed
)

print(
    "Genuine comparisons:",
    len(genuine_scores)
)

print(
    "Impostor comparisons:",
    len(impostor_scores)
)

print()


# ============================================================
# STOP IF NO SCORES
# ============================================================

if (
    len(genuine_scores) == 0
    or
    len(impostor_scores) == 0
):

    print("ERROR: No valid biometric comparisons were generated.")

    print(
        "Please check the embedding/template processing."
    )

    raise SystemExit(1)


# ============================================================
# SCORE STATISTICS
# ============================================================

print("======================================")
print("SCORE STATISTICS")
print("======================================")
print()

print(
    "Genuine mean:",
    f"{np.mean(genuine_scores):.4f}"
)

print(
    "Genuine median:",
    f"{np.median(genuine_scores):.4f}"
)

print(
    "Genuine minimum:",
    f"{np.min(genuine_scores):.4f}"
)

print()

print(
    "Impostor mean:",
    f"{np.mean(impostor_scores):.4f}"
)

print(
    "Impostor median:",
    f"{np.median(impostor_scores):.4f}"
)

print(
    "Impostor maximum:",
    f"{np.max(impostor_scores):.4f}"
)

print()


# ============================================================
# THRESHOLD ANALYSIS
# ============================================================

results = []

for threshold in BIOMETRIC_THRESHOLDS:

    genuine_accepted = np.sum(
        genuine_scores >= threshold
    )

    genuine_rejected = np.sum(
        genuine_scores < threshold
    )

    impostor_accepted = np.sum(
        impostor_scores >= threshold
    )

    impostor_rejected = np.sum(
        impostor_scores < threshold
    )


    frr = (
        genuine_rejected /
        len(genuine_scores)
    )

    far = (
        impostor_accepted /
        len(impostor_scores)
    )

    tar = (
        genuine_accepted /
        len(genuine_scores)
    )


    results.append(
        (
            threshold,
            far,
            frr,
            tar
        )
    )


# ============================================================
# CONVERT RESULTS
# ============================================================

results_array = np.array(
    results
)

threshold_values = results_array[:, 0]
far_values = results_array[:, 1]
frr_values = results_array[:, 2]
tar_values = results_array[:, 3]


# ============================================================
# EER
# ============================================================

eer_index = np.argmin(
    np.abs(
        far_values -
        frr_values
    )
)

eer_threshold = (
    threshold_values[eer_index]
)

eer_far = (
    far_values[eer_index]
)

eer_frr = (
    frr_values[eer_index]
)


# ============================================================
# 0.60 THRESHOLD
# ============================================================

current_threshold = 0.60

current_index = np.argmin(
    np.abs(
        threshold_values -
        current_threshold
    )
)

current_far = (
    far_values[current_index]
)

current_frr = (
    frr_values[current_index]
)

current_tar = (
    tar_values[current_index]
)


# ============================================================
# 0.70 THRESHOLD
# ============================================================

security_threshold = 0.70

security_index = np.argmin(
    np.abs(
        threshold_values -
        security_threshold
    )
)

security_far = (
    far_values[security_index]
)

security_frr = (
    frr_values[security_index]
)

security_tar = (
    tar_values[security_index]
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("======================================")
print("VERIFICATION RESULTS")
print("======================================")
print()

print("THRESHOLD = 0.60")
print("----------------")

print(
    f"FAR: {current_far * 100:.4f}%"
)

print(
    f"FRR: {current_frr * 100:.4f}%"
)

print(
    f"TAR: {current_tar * 100:.4f}%"
)

print()

print("THRESHOLD = 0.70")
print("----------------")

print(
    f"FAR: {security_far * 100:.4f}%"
)

print(
    f"FRR: {security_frr * 100:.4f}%"
)

print(
    f"TAR: {security_tar * 100:.4f}%"
)

print()

print("EER APPROXIMATION")
print("-----------------")

print(
    f"Threshold: {eer_threshold:.2f}"
)

print(
    f"FAR: {eer_far * 100:.4f}%"
)

print(
    f"FRR: {eer_frr * 100:.4f}%"
)

print()


# ============================================================
# SAVE RESULTS
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "Threshold",
            "FAR",
            "FRR",
            "TAR"
        ]
    )

    for row in results:

        writer.writerow(row)


# ============================================================
# FINISH
# ============================================================

print("======================================")
print("EVALUATION COMPLETED")
print("======================================")
print()

print(
    "Results saved:",
    OUTPUT_FILE
)

print()

print("======================================")