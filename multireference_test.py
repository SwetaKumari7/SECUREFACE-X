import os
import numpy as np
from face_engine import get_embedding


TESTING_DIR = r"dataset\FEI_DATABASE\TESTING"
TEMPLATE_FILE = r"models\face_templates_multi.pkl"

import pickle


def cosine_similarity(embedding1, embedding2):

    embedding1 = np.asarray(embedding1)
    embedding2 = np.asarray(embedding2)

    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(
        np.dot(embedding1, embedding2)
        / (norm1 * norm2)
    )


def multi_reference_similarity(
    test_embedding,
    reference_embeddings
):

    scores = []

    for reference in reference_embeddings:

        score = cosine_similarity(
            test_embedding,
            reference
        )

        scores.append(score)

    scores = np.asarray(scores)

    maximum_score = float(
        np.max(scores)
    )

    mean_score = float(
        np.mean(scores)
    )

    # Average of the two strongest references
    top_k = min(2, len(scores))

    top_scores = np.sort(scores)[-top_k:]

    top_mean_score = float(
        np.mean(top_scores)
    )

    return (
        maximum_score,
        mean_score,
        top_mean_score
    )


def main():

    print("======================================")
    print("MULTI-REFERENCE MATCHING TEST")
    print("======================================")
    print()

    with open(
        TEMPLATE_FILE,
        "rb"
    ) as file:

        templates = pickle.load(file)

    print(
        "Registered subjects:",
        len(templates)
    )

    print(
        "References per subject: 5"
    )

    print()

    total = 0
    correct = 0
    skipped = 0

    results = []

    subjects = sorted(
        templates.keys()
    )

    for subject_id in subjects:

        subject_path = os.path.join(
            TESTING_DIR,
            subject_id
        )

        if not os.path.isdir(subject_path):
            continue

        for image_file in sorted(
            os.listdir(subject_path)
        ):

            if not image_file.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            total += 1

            image_path = os.path.join(
                subject_path,
                image_file
            )

            try:

                test_embedding = get_embedding(
                    image_path
                )

            except Exception as error:

                skipped += 1

                print(
                    f"Skipped: "
                    f"{subject_id}/{image_file}"
                )

                continue

            best_subject = None
            best_score = -1.0
            best_mean = 0.0
            best_top_mean = 0.0

            for registered_subject in subjects:

                references = templates[
                    registered_subject
                ]["embeddings"]

                (
                    maximum_score,
                    mean_score,
                    top_mean_score
                ) = multi_reference_similarity(
                    test_embedding,
                    references
                )

                if maximum_score > best_score:

                    best_score = maximum_score

                    best_subject = (
                        registered_subject
                    )

                    best_mean = mean_score

                    best_top_mean = (
                        top_mean_score
                    )

            if best_subject == subject_id:

                correct += 1

            results.append({
                "actual": subject_id,
                "predicted": best_subject,
                "max_similarity": best_score,
                "mean_similarity": best_mean,
                "top2_mean_similarity": best_top_mean
            })

    tested = total - skipped

    accuracy = (
        correct / tested * 100
        if tested > 0
        else 0
    )

    print()
    print("======================================")
    print("MULTI-REFERENCE RESULTS")
    print("======================================")

    print(
        "Total images:",
        total
    )

    print(
        "Tested images:",
        tested
    )

    print(
        "Skipped images:",
        skipped
    )

    print(
        "Correct predictions:",
        correct
    )

    print(
        "Identification Accuracy:",
        f"{accuracy:.2f}%"
    )

    print()
    print("======================================")
    print("MATCHING METHOD")
    print("======================================")

    print(
        "References per subject: 5"
    )

    print(
        "Decision score: Maximum similarity"
    )

    print(
        "Additional metrics: Mean similarity"
    )

    print(
        "Additional metrics: Top-2 mean similarity"
    )

    print("======================================")


if __name__ == "__main__":
    main()