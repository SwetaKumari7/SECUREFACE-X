import os
import pickle
import numpy as np

from face_engine import get_embedding


TRAINING_DIR = r"dataset\FEI_DATABASE\TRAINING"
OUTPUT_FILE = r"models\face_templates_multi.pkl"

MAX_REFERENCES = 5


def normalize_embedding(embedding):
    embedding = np.asarray(embedding, dtype=np.float32)

    norm = np.linalg.norm(embedding)

    if norm == 0:
        raise ValueError("Invalid embedding.")

    return embedding / norm


def build_templates():

    templates = {}

    total_images = 0
    successful_images = 0
    skipped_images = 0

    print("======================================")
    print("MULTI-REFERENCE BIOMETRIC TRAINING")
    print("======================================")
    print()

    subjects = sorted(
        os.listdir(TRAINING_DIR)
    )

    for subject_id in subjects:

        subject_path = os.path.join(
            TRAINING_DIR,
            subject_id
        )

        if not os.path.isdir(subject_path):
            continue

        print(
            f"Processing subject: {subject_id}"
        )

        embeddings = []

        image_files = sorted(
            os.listdir(subject_path)
        )

        for image_file in image_files:

            if not image_file.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            total_images += 1

            image_path = os.path.join(
                subject_path,
                image_file
            )

            try:

                embedding = get_embedding(
                    image_path
                )

                embedding = normalize_embedding(
                    embedding
                )

                embeddings.append(
                    embedding
                )

                successful_images += 1

            except Exception as error:

                skipped_images += 1

                print(
                    f"  Skipped: {image_file}"
                )

                print(
                    f"  Reason: {error}"
                )

        if len(embeddings) == 0:

            print(
                "  WARNING: No valid embeddings."
            )

            continue

        # Keep at most MAX_REFERENCES
        selected_embeddings = embeddings[
            :MAX_REFERENCES
        ]

        templates[subject_id] = {
            "embeddings": selected_embeddings,
            "template_count": len(
                selected_embeddings
            )
        }

        print(
            f"  References stored: "
            f"{len(selected_embeddings)}"
        )

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "wb"
    ) as file:

        pickle.dump(
            templates,
            file
        )

    print()
    print("======================================")
    print("TRAINING COMPLETED")
    print("======================================")

    print(
        "Total images:",
        total_images
    )

    print(
        "Successful images:",
        successful_images
    )

    print(
        "Skipped images:",
        skipped_images
    )

    print(
        "Registered subjects:",
        len(templates)
    )

    print(
        "Maximum references per subject:",
        MAX_REFERENCES
    )

    print()
    print(
        "Template file:",
        OUTPUT_FILE
    )

    print("======================================")


if __name__ == "__main__":
    build_templates()