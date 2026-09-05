import os
import pickle
import numpy as np

from face_engine import get_embedding


# --------------------------------------------------
# Paths
# --------------------------------------------------

TRAIN_DIR = r"dataset\FEI_DATABASE\TRAINING"
MODEL_DIR = r"models"
OUTPUT_FILE = os.path.join(MODEL_DIR, "face_templates.pkl")


# --------------------------------------------------
# Create models folder
# --------------------------------------------------

os.makedirs(MODEL_DIR, exist_ok=True)


# --------------------------------------------------
# Generate biometric templates
# --------------------------------------------------

def train():

    templates = {}

    subjects = sorted(
        [
            folder
            for folder in os.listdir(TRAIN_DIR)
            if os.path.isdir(os.path.join(TRAIN_DIR, folder))
        ]
    )

    print("Subjects found:", len(subjects))
    print()

    for index, subject in enumerate(subjects, start=1):

        subject_path = os.path.join(TRAIN_DIR, subject)

        image_files = sorted(
            [
                file
                for file in os.listdir(subject_path)
                if file.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
        )

        embeddings = []

        print(
            f"[{index:03d}/{len(subjects):03d}] "
            f"Subject {subject} - {len(image_files)} images"
        )

        for image_file in image_files:

            image_path = os.path.join(subject_path, image_file)

            try:

                embedding = get_embedding(image_path)
                embeddings.append(embedding)

            except Exception as error:

                print(
                    f"    Skipped {image_file}: {error}"
                )

        if embeddings:

            # Average all embeddings for this subject
            template = np.mean(embeddings, axis=0)

            # Normalize template
            norm = np.linalg.norm(template)

            if norm > 0:
                template = template / norm

            templates[subject] = template

    # --------------------------------------------------
    # Save templates
    # --------------------------------------------------

    with open(OUTPUT_FILE, "wb") as file:
        pickle.dump(templates, file)

    print()
    print("======================================")
    print("TRAINING COMPLETED")
    print("Subjects processed:", len(templates))
    print("Templates saved:", OUTPUT_FILE)
    print("======================================")


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    train()