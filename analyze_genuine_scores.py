import os
import csv
import numpy as np

from face_engine import get_embedding
from security import load_encrypted_templates


# ============================================================
# CONFIGURATION
# ============================================================

TEST_DIR = r"dataset\FEI_DATABASE\TESTING"

OUTPUT_FILE = "low_genuine_scores.csv"

LOW_SCORE_LIMIT = 0.60


# ============================================================
# LOAD TEMPLATES
# ============================================================

print("======================================")
print("LOW GENUINE SCORE ANALYSIS")
print("======================================")
print()

print("Loading encrypted templates...")

templates = load_encrypted_templates()

print("Registered subjects:", len(templates))
print()


# ============================================================
# STORAGE
# ============================================================

results = []

total_images = 0
successful = 0
skipped = 0


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
# PROCESS IMAGES
# ============================================================

for subject in subjects:

    subject_path = os.path.join(
        TEST_DIR,
        subject
    )

    image_files = sorted(
        [
            file
            for file in os.listdir(subject_path)
            if file.lower().endswith(
                (".jpg", ".jpeg", ".png")
            )
        ]
    )

    for image_file in image_files:

        total_images += 1

        image_path = os.path.join(
            subject_path,
            image_file
        )

        try:

            embedding = get_embedding(
                image_path
            )

            template = templates[subject]

            similarity = float(
                np.dot(
                    embedding,
                    template
                )
            )

            successful += 1

            results.append(
                {
                    "subject": subject,
                    "image": image_file,
                    "path": image_path,
                    "similarity": similarity
                }
            )

        except Exception as error:

            skipped += 1

            print(
                f"Skipped: {image_path}"
            )

            print(
                "Reason:",
                error
            )


# ============================================================
# SORT FROM LOWEST TO HIGHEST
# ============================================================

results.sort(
    key=lambda x: x["similarity"]
)


# ============================================================
# DISPLAY LOWEST SCORES
# ============================================================

print()
print("======================================")
print("LOWEST GENUINE SCORES")
print("======================================")
print()

for item in results[:30]:

    print(
        f"{item['similarity']:.4f} | "
        f"Subject: {item['subject']} | "
        f"Image: {item['image']}"
    )


# ============================================================
# COUNT SCORES BELOW DIFFERENT THRESHOLDS
# ============================================================

scores = np.array(
    [
        item["similarity"]
        for item in results
    ]
)


print()
print("======================================")
print("GENUINE SCORE BREAKDOWN")
print("======================================")
print()

for threshold in [
    0.30,
    0.40,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90
]:

    count = np.sum(
        scores < threshold
    )

    percentage = (
        count / len(scores)
    ) * 100

    print(
        f"Below {threshold:.2f}: "
        f"{count} images "
        f"({percentage:.4f}%)"
    )


# ============================================================
# SAVE LOW-SCORE RESULTS
# ============================================================

low_scores = [
    item
    for item in results
    if item["similarity"] < LOW_SCORE_LIMIT
]


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "Subject",
            "Image",
            "Path",
            "Similarity"
        ]
    )

    for item in low_scores:

        writer.writerow(
            [
                item["subject"],
                item["image"],
                item["path"],
                f"{item['similarity']:.6f}"
            ]
        )


# ============================================================
# SUMMARY
# ============================================================

print()
print("======================================")
print("ANALYSIS COMPLETED")
print("======================================")
print()

print(
    "Total images:",
    total_images
)

print(
    "Successful:",
    successful
)

print(
    "Skipped:",
    skipped
)

print(
    "Low-score images:",
    len(low_scores)
)

print()

print(
    "Saved:",
    OUTPUT_FILE
)

print()

print("======================================")