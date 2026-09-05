import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score


INPUT_FILE = "multireference_verification_scores.csv"


def calculate_metrics(
    genuine_scores,
    impostor_scores,
    threshold
):

    tp = np.sum(genuine_scores >= threshold)
    fn = np.sum(genuine_scores < threshold)

    fp = np.sum(impostor_scores >= threshold)
    tn = np.sum(impostor_scores < threshold)

    far = fp / len(impostor_scores)
    frr = fn / len(genuine_scores)

    tar = tp / len(genuine_scores)

    accuracy = (
        (tp + tn) /
        (len(genuine_scores) + len(impostor_scores))
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )

    recall = tar

    f1 = (
        2 * precision * recall /
        (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {
        "threshold": threshold,
        "FAR": far,
        "FRR": frr,
        "TAR": tar,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1
    }


def find_best_threshold(
    genuine_scores,
    impostor_scores
):

    thresholds = np.linspace(
        0.0,
        1.0,
        1001
    )

    best = None

    for threshold in thresholds:

        metrics = calculate_metrics(
            genuine_scores,
            impostor_scores,
            threshold
        )

        if (
            best is None
            or metrics["F1"] > best["F1"]
        ):

            best = metrics

    return best


def find_eer(
    genuine_scores,
    impostor_scores
):

    thresholds = np.linspace(
        0.0,
        1.0,
        1001
    )

    best_threshold = 0
    best_far = 0
    best_frr = 0
    smallest_difference = float("inf")

    for threshold in thresholds:

        fp = np.sum(
            impostor_scores >= threshold
        )

        fn = np.sum(
            genuine_scores < threshold
        )

        far = (
            fp /
            len(impostor_scores)
        )

        frr = (
            fn /
            len(genuine_scores)
        )

        difference = abs(far - frr)

        if difference < smallest_difference:

            smallest_difference = difference

            best_threshold = threshold
            best_far = far
            best_frr = frr

    return (
        best_threshold,
        best_far,
        best_frr
    )


def evaluate_method(
    name,
    genuine_scores,
    impostor_scores
):

    print()
    print("======================================")
    print(name)
    print("======================================")

    # Fixed threshold
    fixed = calculate_metrics(
        genuine_scores,
        impostor_scores,
        0.62
    )

    print()
    print("At threshold 0.62:")

    print(
        "FAR:",
        f"{fixed['FAR'] * 100:.4f}%"
    )

    print(
        "FRR:",
        f"{fixed['FRR'] * 100:.4f}%"
    )

    print(
        "TAR:",
        f"{fixed['TAR'] * 100:.4f}%"
    )

    print(
        "F1:",
        f"{fixed['F1'] * 100:.4f}%"
    )

    # Best F1 threshold
    best = find_best_threshold(
        genuine_scores,
        impostor_scores
    )

    print()
    print("Best F1 threshold:")

    print(
        "Threshold:",
        f"{best['threshold']:.3f}"
    )

    print(
        "FAR:",
        f"{best['FAR'] * 100:.4f}%"
    )

    print(
        "FRR:",
        f"{best['FRR'] * 100:.4f}%"
    )

    print(
        "TAR:",
        f"{best['TAR'] * 100:.4f}%"
    )

    print(
        "F1:",
        f"{best['F1'] * 100:.4f}%"
    )

    # EER
    (
        eer_threshold,
        eer_far,
        eer_frr
    ) = find_eer(
        genuine_scores,
        impostor_scores
    )

    print()
    print("EER:")

    print(
        "Threshold:",
        f"{eer_threshold:.3f}"
    )

    print(
        "FAR:",
        f"{eer_far * 100:.4f}%"
    )

    print(
        "FRR:",
        f"{eer_frr * 100:.4f}%"
    )

    # AUC
    y_true = np.concatenate([
        np.ones(len(genuine_scores)),
        np.zeros(len(impostor_scores))
    ])

    y_scores = np.concatenate([
        genuine_scores,
        impostor_scores
    ])

    auc = roc_auc_score(
        y_true,
        y_scores
    )

    print()
    print(
        "ROC-AUC:",
        f"{auc * 100:.4f}%"
    )

    return {
        "Method": name,
        "FAR_0.62": fixed["FAR"],
        "FRR_0.62": fixed["FRR"],
        "TAR_0.62": fixed["TAR"],
        "F1_0.62": fixed["F1"],
        "Best_F1_Threshold":
            best["threshold"],
        "Best_F1":
            best["F1"],
        "EER_Threshold":
            eer_threshold,
        "EER_FAR":
            eer_far,
        "EER_FRR":
            eer_frr,
        "ROC_AUC":
            auc
    }


def main():

    print("======================================")
    print("MULTI-REFERENCE METHOD COMPARISON")
    print("======================================")

    df = pd.read_csv(
        INPUT_FILE
    )

    print()
    print(
        "Rows loaded:",
        len(df)
    )

    # --------------------------------
    # IMPORTANT:
    # The CSV contains the MAX score.
    # --------------------------------

    genuine_max = df[
        df["type"] == "genuine"
    ]["score"].values

    impostor_max = df[
        df["type"] == "impostor"
    ]["score"].values

    results = []

    # Method 1
    results.append(
        evaluate_method(
            "METHOD 1 - MAXIMUM SIMILARITY",
            genuine_max,
            impostor_max
        )
    )

    # --------------------------------
    # Method 2
    #
    # Conservative transformation.
    #
    # Penalize scores below 0.80.
    # --------------------------------

    genuine_consistency = (
        0.6 * genuine_max
        + 0.4 * np.minimum(
            genuine_max,
            0.80
        )
    )

    impostor_consistency = (
        0.6 * impostor_max
        + 0.4 * np.minimum(
            impostor_max,
            0.80
        )
    )

    results.append(
        evaluate_method(
            "METHOD 2 - CONSISTENCY PENALIZED",
            genuine_consistency,
            impostor_consistency
        )
    )

    # --------------------------------
    # Method 3
    #
    # Logarithmic compression of
    # very high similarities.
    # --------------------------------

    genuine_log = np.sign(
        genuine_max
    ) * np.sqrt(
        np.maximum(
            genuine_max,
            0
        )
    )

    impostor_log = np.sign(
        impostor_max
    ) * np.sqrt(
        np.maximum(
            impostor_max,
            0
        )
    )

    results.append(
        evaluate_method(
            "METHOD 3 - COMPRESSED SCORE",
            genuine_log,
            impostor_log
        )
    )

    # --------------------------------
    # Summary
    # --------------------------------

    summary = pd.DataFrame(
        results
    )

    summary.to_csv(
        "multireference_method_comparison.csv",
        index=False
    )

    print()
    print("======================================")
    print("FINAL COMPARISON")
    print("======================================")

    print()

    print(
        summary[
            [
                "Method",
                "FAR_0.62",
                "FRR_0.62",
                "TAR_0.62",
                "Best_F1",
                "EER_FAR",
                "ROC_AUC"
            ]
        ].to_string(
            index=False
        )
    )

    print()
    print(
        "Results saved to:"
    )

    print(
        "multireference_method_comparison.csv"
    )

    print("======================================")


if __name__ == "__main__":
    main()