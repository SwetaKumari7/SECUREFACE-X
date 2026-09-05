import os

from face_engine import get_embedding
from security import load_encrypted_templates, cosine_similarity


TESTING_DIR = r"dataset\FEI_DATABASE\TESTING"


def test():

    print("======================================")
    print("FACE IDENTIFICATION TEST")
    print("======================================")

    print("Loading encrypted biometric templates...")

    templates = load_encrypted_templates()

    print("Registered subjects:", len(templates))
    print()

    total_images = 0
    tested_images = 0
    skipped_images = 0
    correct_predictions = 0

    subjects = sorted(
        [
            folder
            for folder in os.listdir(TESTING_DIR)
            if os.path.isdir(
                os.path.join(TESTING_DIR, folder)
            )
        ]
    )

    for subject_id in subjects:

        subject_path = os.path.join(
            TESTING_DIR,
            subject_id
        )

        images = sorted(
            [
                file
                for file in os.listdir(subject_path)
                if file.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                )
            ]
        )

        for image_name in images:

            total_images += 1

            image_path = os.path.join(
                subject_path,
                image_name
            )

            try:

                embedding = get_embedding(
                    image_path
                )

            except Exception as error:

                skipped_images += 1

                print(
                    f"Skipped {subject_id}/{image_name}: "
                    f"{error}"
                )

                continue

            tested_images += 1

            best_subject = None
            best_score = -1.0

            for registered_subject, template in templates.items():

                score = cosine_similarity(
                    embedding,
                    template
                )

                if score > best_score:

                    best_score = score
                    best_subject = registered_subject

            if best_subject == subject_id:

                correct_predictions += 1

            else:

                print(
                    f"Wrong prediction: "
                    f"Actual={subject_id}, "
                    f"Predicted={best_subject}, "
                    f"Similarity={best_score:.4f}"
                )

    print()
    print("======================================")
    print("IDENTIFICATION TEST COMPLETED")
    print("======================================")

    print("Total images:", total_images)
    print("Tested images:", tested_images)
    print("Skipped images:", skipped_images)
    print("Correct predictions:", correct_predictions)

    if tested_images > 0:

        accuracy = (
            correct_predictions
            / tested_images
        ) * 100

        print(
            f"Identification Accuracy: "
            f"{accuracy:.2f}%"
        )

    print("======================================")


if __name__ == "__main__":

    test()