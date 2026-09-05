import os
import pickle
import numpy as np
import pandas as pd

from face_engine import get_embedding


TESTING_DIR = r"dataset\FEI_DATABASE\TESTING"
TEMPLATE_FILE = r"models\face_templates_multi.pkl"

OUTPUT_CSV = "multireference_verification_scores.csv"


def cosine_similarity(a, b):

    a = np.asarray(a)
    b = np.asarray(b)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(
        np.dot(a, b) /
        (norm_a * norm_b)
    )


def calculate_scores(
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

    maximum = float(
        np.max(scores)
    )

    top_k = min(2, len(scores))

    top_two = np.sort(scores)[-top_k:]

    top2_mean = float(
        np.mean(top_two)
    )

    mean = float(
        np.mean(scores)
    )

    return maximum, mean, top2_mean


def main():

    print("======================================")
    print("MULTI-REFERENCE SECURITY EVALUATION")
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

    subjects = sorted(
        templates.keys()
    )

    genuine_scores = []
    impostor_scores = []

    rows = []

    skipped = 0

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

            image_path = os.path.join(
                subject_path,
                image_file
            )

            try:

                test_embedding = get_embedding(
                    image_path
                )

            except Exception:

                skipped += 1
                continue

            # --------------------------------
            # GENUINE COMPARISON
            # --------------------------------

            genuine_refs = templates[
                subject_id
            ]["embeddings"]

            (
                genuine_max,
                genuine_mean,
                genuine_top2
            ) = calculate_scores(
                test_embedding,
                genuine_refs
            )

            genuine_scores.append(
                genuine_max
            )

            rows.append({
                "type": "genuine",
                "subject": subject_id,
                "image": image_file,
                "score": genuine_max
            })

            # --------------------------------
            # IMPOSTOR COMPARISONS
            # --------------------------------

            for other_subject in subjects:

                if other_subject == subject_id:
                    continue

                impostor_refs = templates[
                    other_subject
                ]["embeddings"]

                (
                    impostor_max,
                    impostor_mean,
                    impostor_top2
                ) = calculate_scores(
                    test_embedding,
                    impostor_refs
                )

                impostor_scores.append(
                    impostor_max
                )

                rows.append({
                    "type": "impostor",
                    "subject": subject_id,
                    "image": image_file,
                    "comparison_subject":
                        other_subject,
                    "score": impostor_max
                })

    genuine_scores = np.asarray(
        genuine_scores
    )

    impostor_scores = np.asarray(
        impostor_scores
    )

    print()
    print("======================================")
    print("SCORE STATISTICS")
    print("======================================")

    print(
        "Genuine comparisons:",
        len(genuine_scores)
    )

    print(
        "Impostor comparisons:",
        len(impostor_scores)
    )

    print()

    print(
        "Genuine minimum:",
        f"{np.min(genuine_scores):.4f}"
    )

    print(
        "Genuine maximum:",
        f"{np.max(genuine_scores):.4f}"
    )

    print(
        "Genuine mean:",
        f"{np.mean(genuine_scores):.4f}"
    )

    print(
        "Genuine median:",
        f"{np.median(genuine_scores):.4f}"
    )

    print()

    print(
        "Impostor minimum:",
        f"{np.min(impostor_scores):.4f}"
    )

    print(
        "Impostor maximum:",
        f"{np.max(impostor_scores):.4f}"
    )

    print(
        "Impostor mean:",
        f"{np.mean(impostor_scores):.4f}"
    )

    print(
        "Impostor median:",
        f"{np.median(impostor_scores):.4f}"
    )

    # --------------------------------
    # THRESHOLD ANALYSIS
    # --------------------------------

    thresholds = np.linspace(
        0.0,
        1.0,
        1001
    )

    best_accuracy = 0
    best_accuracy_threshold = 0

    best_f1 = 0
    best_f1_threshold = 0

    eer_difference = float("inf")
    eer_threshold = 0
    eer_far = 0
    eer_frr = 0

    total = (
        len(genuine_scores)
        + len(impostor_scores)
    )

    for threshold in thresholds:

        false_accepts = np.sum(
            impostor_scores >= threshold
        )

        false_rejects = np.sum(
            genuine_scores < threshold
        )

        true_accepts = np.sum(
            genuine_scores >= threshold
        )

        true_rejects = np.sum(
            impostor_scores < threshold
        )

        far = (
            false_accepts /
            len(impostor_scores)
        )

        frr = (
            false_rejects /
            len(genuine_scores)
        )

        accuracy = (
            true_accepts +
            true_rejects
        ) / total

        precision_denominator = (
            true_accepts +
            false_accepts
        )

        recall = (
            true_accepts /
            len(genuine_scores)
        )

        if precision_denominator > 0:

            precision = (
                true_accepts /
                precision_denominator
            )

        else:

            precision = 0

        if (
            precision + recall
            > 0
        ):

            f1 = (
                2 *
                precision *
                recall /
                (precision + recall)
            )

        else:

            f1 = 0

        if accuracy > best_accuracy:

            best_accuracy = accuracy
            best_accuracy_threshold = threshold

        if f1 > best_f1:

            best_f1 = f1
            best_f1_threshold = threshold

        difference = abs(
            far - frr
        )

        if difference < eer_difference:

            eer_difference = difference
            eer_threshold = threshold
            eer_far = far
            eer_frr = frr

    # --------------------------------
    # ROC AUC
    # --------------------------------

    try:

        from sklearn.metrics import roc_auc_score

        y_true = np.concatenate([
            np.ones(
                len(genuine_scores)
            ),
            np.zeros(
                len(impostor_scores)
            )
        ])

        y_scores = np.concatenate([
            genuine_scores,
            impostor_scores
        ])

        auc = roc_auc_score(
            y_true,
            y_scores
        )

    except Exception:

        auc = 0

    # --------------------------------
    # SELECTED THRESHOLD
    # --------------------------------

    selected_threshold = 0.62

    false_accepts = np.sum(
        impostor_scores >=
        selected_threshold
    )

    false_rejects = np.sum(
        genuine_scores <
        selected_threshold
    )

    true_accepts = np.sum(
        genuine_scores >=
        selected_threshold
    )

    true_rejects = np.sum(
        impostor_scores <
        selected_threshold
    )

    far = (
        false_accepts /
        len(impostor_scores)
    )

    frr = (
        false_rejects /
        len(genuine_scores)
    )

    tar = (
        true_accepts /
        len(genuine_scores)
    )

    accuracy = (
        true_accepts +
        true_rejects
    ) / total

    precision_denominator = (
        true_accepts +
        false_accepts
    )

    precision = (
        true_accepts /
        precision_denominator
        if precision_denominator > 0
        else 0
    )

    recall = tar

    f1 = (
        2 *
        precision *
        recall /
        (precision + recall)
        if precision + recall > 0
        else 0
    )

    # --------------------------------
    # SAVE RAW SCORES
    # --------------------------------

    dataframe = pd.DataFrame(rows)

    dataframe.to_csv(
        OUTPUT_CSV,
        index=False
    )

    # --------------------------------
    # RESULTS
    # --------------------------------

    print()
    print("======================================")
    print("SELECTED THRESHOLD: 0.62")
    print("======================================")

    print(
        "FAR:",
        f"{far * 100:.4f}%"
    )

    print(
        "FRR:",
        f"{frr * 100:.4f}%"
    )

    print(
        "TAR:",
        f"{tar * 100:.4f}%"
    )

    print(
        "Accuracy:",
        f"{accuracy * 100:.4f}%"
    )

    print(
        "Precision:",
        f"{precision * 100:.4f}%"
    )

    print(
        "Recall:",
        f"{recall * 100:.4f}%"
    )

    print(
        "F1:",
        f"{f1 * 100:.4f}%"
    )

    print()
    print("======================================")
    print("EER")
    print("======================================")

    print(
        "EER threshold:",
        f"{eer_threshold:.3f}"
    )

    print(
        "FAR at EER:",
        f"{eer_far * 100:.4f}%"
    )

    print(
        "FRR at EER:",
        f"{eer_frr * 100:.4f}%"
    )

    print()
    print("======================================")
    print("BEST THRESHOLDS")
    print("======================================")

    print(
        "Best accuracy threshold:",
        f"{best_accuracy_threshold:.3f}"
    )

    print(
        "Best accuracy:",
        f"{best_accuracy * 100:.4f}%"
    )

    print(
        "Best F1 threshold:",
        f"{best_f1_threshold:.3f}"
    )

    print(
        "Best F1:",
        f"{best_f1 * 100:.4f}%"
    )

    print()
    print("ROC-AUC:")

    print(
        f"{auc * 100:.4f}%"
    )

    print()
    print(
        "Skipped images:",
        skipped
    )

    print()
    print(
        "Results saved to:",
        OUTPUT_CSV
    )

    print("======================================")


if __name__ == "__main__":
    main()