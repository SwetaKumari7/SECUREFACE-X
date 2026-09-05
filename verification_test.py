import os
import csv
import numpy as np
import matplotlib.pyplot as plt

from face_engine import get_embedding
from security import load_encrypted_templates


# ============================================================
# CONFIGURATION
# ============================================================

TEST_DIR = r"dataset\FEI_DATABASE\TESTING"

# Threshold range
THRESHOLDS = np.arange(0.30, 0.96, 0.01)

# Current application threshold
CURRENT_THRESHOLD = 0.62

# Output files
SCORES_FILE = "verification_scores.csv"
RESULTS_FILE = "verification_results.csv"

ROC_GRAPH = "roc_curve.png"
FAR_FRR_GRAPH = "far_frr_curve.png"
DISTRIBUTION_GRAPH = "similarity_distribution.png"
CONFUSION_GRAPH = "confusion_matrix.png"
F1_GRAPH = "f1_score_curve.png"
PRECISION_RECALL_GRAPH = "precision_recall_curve.png"


# ============================================================
# LOAD ENCRYPTED BIOMETRIC TEMPLATES
# ============================================================

print("======================================")
print("BIOMETRIC VERIFICATION EVALUATION")
print("======================================")
print()

print("Loading encrypted biometric templates...")

templates = load_encrypted_templates()

print("Registered subjects:", len(templates))
print()


# ============================================================
# STORAGE
# ============================================================

genuine_scores = []
impostor_scores = []

# Detailed score records
score_records = []

total_images = 0
successful_embeddings = 0
skipped_images = 0


# ============================================================
# GET SUBJECT FOLDERS
# ============================================================

subjects = sorted(
    [
        folder
        for folder in os.listdir(TEST_DIR)
        if os.path.isdir(os.path.join(TEST_DIR, folder))
    ]
)

print("Testing subjects:", len(subjects))
print()


# ============================================================
# PROCESS TESTING IMAGES
# ============================================================

for subject_index, subject in enumerate(subjects, start=1):

    subject_path = os.path.join(TEST_DIR, subject)

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

            # ------------------------------------------------
            # Generate FaceNet embedding
            # ------------------------------------------------

            embedding = get_embedding(image_path)

            successful_embeddings += 1

            # ------------------------------------------------
            # Genuine comparison
            # Same person's image vs same person's template
            # ------------------------------------------------

            genuine_template = templates[subject]

            genuine_score = float(
                np.dot(
                    embedding,
                    genuine_template
                )
            )

            genuine_scores.append(genuine_score)

            score_records.append(
                {
                    "Subject": subject,
                    "Image": image_file,
                    "Comparison": "Genuine",
                    "Compared_With": subject,
                    "Score": genuine_score,
                    "Label": 1
                }
            )

            # ------------------------------------------------
            # Impostor comparisons
            # Image vs every other person's template
            # ------------------------------------------------

            for other_subject, other_template in templates.items():

                if other_subject == subject:
                    continue

                impostor_score = float(
                    np.dot(
                        embedding,
                        other_template
                    )
                )

                impostor_scores.append(impostor_score)

                score_records.append(
                    {
                        "Subject": subject,
                        "Image": image_file,
                        "Comparison": "Impostor",
                        "Compared_With": other_subject,
                        "Score": impostor_score,
                        "Label": 0
                    }
                )

        except Exception as error:

            skipped_images += 1

            print(
                f"Skipped {subject}/{image_file}: "
                f"{error}"
            )

    # --------------------------------------------------------
    # Progress
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
    dtype=float
)

impostor_scores = np.array(
    impostor_scores,
    dtype=float
)


# ============================================================
# BASIC INFORMATION
# ============================================================

print()
print("======================================")
print("SCORE COLLECTION COMPLETED")
print("======================================")

print("Total testing images:", total_images)

print(
    "Successful embeddings:",
    successful_embeddings
)

print(
    "Skipped images:",
    skipped_images
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
# SCORE STATISTICS
# ============================================================

print("======================================")
print("SIMILARITY SCORE STATISTICS")
print("======================================")

print()
print("GENUINE MATCH SCORES")
print("--------------------")

print(
    f"Minimum : {np.min(genuine_scores):.4f}"
)

print(
    f"Maximum : {np.max(genuine_scores):.4f}"
)

print(
    f"Mean    : {np.mean(genuine_scores):.4f}"
)

print(
    f"Median  : {np.median(genuine_scores):.4f}"
)

print()

print("IMPOSTOR MATCH SCORES")
print("---------------------")

print(
    f"Minimum : {np.min(impostor_scores):.4f}"
)

print(
    f"Maximum : {np.max(impostor_scores):.4f}"
)

print(
    f"Mean    : {np.mean(impostor_scores):.4f}"
)

print(
    f"Median  : {np.median(impostor_scores):.4f}"
)

print()


# ============================================================
# SAVE INDIVIDUAL SCORES
# ============================================================

print("Saving individual verification scores...")

with open(
    SCORES_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "Subject",
            "Image",
            "Comparison",
            "Compared_With",
            "Score",
            "Label"
        ]
    )

    for record in score_records:

        writer.writerow(
            [
                record["Subject"],
                record["Image"],
                record["Comparison"],
                record["Compared_With"],
                f'{record["Score"]:.6f}',
                record["Label"]
            ]
        )

print(
    "Individual scores saved to:",
    SCORES_FILE
)

print()


# ============================================================
# THRESHOLD EVALUATION
# ============================================================

results = []

for threshold in THRESHOLDS:

    # --------------------------------------------------------
    # Genuine
    # --------------------------------------------------------

    true_positive = np.sum(
        genuine_scores >= threshold
    )

    false_negative = np.sum(
        genuine_scores < threshold
    )

    # --------------------------------------------------------
    # Impostor
    # --------------------------------------------------------

    false_positive = np.sum(
        impostor_scores >= threshold
    )

    true_negative = np.sum(
        impostor_scores < threshold
    )

    # --------------------------------------------------------
    # FAR
    # --------------------------------------------------------

    far = (
        false_positive
        / len(impostor_scores)
    )

    # --------------------------------------------------------
    # FRR
    # --------------------------------------------------------

    frr = (
        false_negative
        / len(genuine_scores)
    )

    # --------------------------------------------------------
    # TAR
    # --------------------------------------------------------

    tar = (
        true_positive
        / len(genuine_scores)
    )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    total_comparisons = (
        len(genuine_scores)
        + len(impostor_scores)
    )

    accuracy = (
        true_positive
        + true_negative
    ) / total_comparisons

    # --------------------------------------------------------
    # Precision
    # --------------------------------------------------------

    if (
        true_positive
        + false_positive
    ) > 0:

        precision = (
            true_positive
            / (
                true_positive
                + false_positive
            )
        )

    else:

        precision = 0.0

    # --------------------------------------------------------
    # Recall
    # --------------------------------------------------------

    if (
        true_positive
        + false_negative
    ) > 0:

        recall = (
            true_positive
            / (
                true_positive
                + false_negative
            )
        )

    else:

        recall = 0.0

    # --------------------------------------------------------
    # F1
    # --------------------------------------------------------

    if (
        precision
        + recall
    ) > 0:

        f1 = (
            2
            * precision
            * recall
            / (
                precision
                + recall
            )
        )

    else:

        f1 = 0.0

    results.append(
        {
            "threshold": threshold,
            "far": far,
            "frr": frr,
            "tar": tar,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": true_positive,
            "tn": true_negative,
            "fp": false_positive,
            "fn": false_negative
        }
    )


# ============================================================
# CONVERT RESULTS
# ============================================================

threshold_values = np.array(
    [r["threshold"] for r in results]
)

far_values = np.array(
    [r["far"] for r in results]
)

frr_values = np.array(
    [r["frr"] for r in results]
)

tar_values = np.array(
    [r["tar"] for r in results]
)

accuracy_values = np.array(
    [r["accuracy"] for r in results]
)

precision_values = np.array(
    [r["precision"] for r in results]
)

recall_values = np.array(
    [r["recall"] for r in results]
)

f1_values = np.array(
    [r["f1"] for r in results]
)


# ============================================================
# EER
# ============================================================

eer_index = np.argmin(
    np.abs(
        far_values
        - frr_values
    )
)

eer_threshold = threshold_values[
    eer_index
]

eer_far = far_values[
    eer_index
]

eer_frr = frr_values[
    eer_index
]


# ============================================================
# BEST ACCURACY
# ============================================================

best_accuracy_index = np.argmax(
    accuracy_values
)

best_accuracy_threshold = (
    threshold_values[
        best_accuracy_index
    ]
)

best_accuracy = (
    accuracy_values[
        best_accuracy_index
    ]
)

best_accuracy_far = (
    far_values[
        best_accuracy_index
    ]
)

best_accuracy_frr = (
    frr_values[
        best_accuracy_index
    ]
)


# ============================================================
# BEST F1
# ============================================================

best_f1_index = np.argmax(
    f1_values
)

best_f1_threshold = (
    threshold_values[
        best_f1_index
    ]
)

best_f1 = (
    f1_values[
        best_f1_index
    ]
)


# ============================================================
# CURRENT THRESHOLD
# ============================================================

current_index = np.argmin(
    np.abs(
        threshold_values
        - CURRENT_THRESHOLD
    )
)

current_result = results[
    current_index
]


# ============================================================
# DISPLAY CURRENT RESULTS
# ============================================================

print("======================================")
print("CURRENT SYSTEM THRESHOLD")
print("======================================")

print(
    f"Threshold : "
    f"{current_result['threshold']:.2f}"
)

print(
    f"FAR       : "
    f"{current_result['far'] * 100:.4f}%"
)

print(
    f"FRR       : "
    f"{current_result['frr'] * 100:.4f}%"
)

print(
    f"TAR       : "
    f"{current_result['tar'] * 100:.4f}%"
)

print(
    f"Accuracy  : "
    f"{current_result['accuracy'] * 100:.4f}%"
)

print(
    f"Precision : "
    f"{current_result['precision'] * 100:.4f}%"
)

print(
    f"Recall    : "
    f"{current_result['recall'] * 100:.4f}%"
)

print(
    f"F1 Score  : "
    f"{current_result['f1'] * 100:.4f}%"
)

print()

print(
    "TP:",
    current_result["tp"]
)

print(
    "TN:",
    current_result["tn"]
)

print(
    "FP:",
    current_result["fp"]
)

print(
    "FN:",
    current_result["fn"]
)

print()


# ============================================================
# BEST ACCURACY
# ============================================================

print("======================================")
print("BEST ACCURACY THRESHOLD")
print("======================================")

print(
    f"Threshold : "
    f"{best_accuracy_threshold:.2f}"
)

print(
    f"Accuracy  : "
    f"{best_accuracy * 100:.4f}%"
)

print(
    f"FAR       : "
    f"{best_accuracy_far * 100:.4f}%"
)

print(
    f"FRR       : "
    f"{best_accuracy_frr * 100:.4f}%"
)

print()


# ============================================================
# BEST F1
# ============================================================

print("======================================")
print("BEST F1 THRESHOLD")
print("======================================")

print(
    f"Threshold : "
    f"{best_f1_threshold:.2f}"
)

print(
    f"F1 Score  : "
    f"{best_f1 * 100:.4f}%"
)

print()


# ============================================================
# EER
# ============================================================

print("======================================")
print("EQUAL ERROR RATE")
print("======================================")

print(
    f"EER Threshold : "
    f"{eer_threshold:.2f}"
)

print(
    f"FAR at EER    : "
    f"{eer_far * 100:.4f}%"
)

print(
    f"FRR at EER    : "
    f"{eer_frr * 100:.4f}%"
)

print()


# ============================================================
# SAVE THRESHOLD RESULTS
# ============================================================

with open(
    RESULTS_FILE,
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
            "TAR",
            "Accuracy",
            "Precision",
            "Recall",
            "F1",
            "TP",
            "TN",
            "FP",
            "FN"
        ]
    )

    for r in results:

        writer.writerow(
            [
                f'{r["threshold"]:.2f}',
                f'{r["far"]:.6f}',
                f'{r["frr"]:.6f}',
                f'{r["tar"]:.6f}',
                f'{r["accuracy"]:.6f}',
                f'{r["precision"]:.6f}',
                f'{r["recall"]:.6f}',
                f'{r["f1"]:.6f}',
                r["tp"],
                r["tn"],
                r["fp"],
                r["fn"]
            ]
        )

print(
    "Threshold results saved to:",
    RESULTS_FILE
)

print()


# ============================================================
# ROC CURVE
# ============================================================

# For biometric verification:
# False Positive Rate = FAR
# True Positive Rate = TAR

plt.figure(figsize=(10, 6))

plt.plot(
    far_values * 100,
    tar_values * 100,
    linewidth=2,
    label="ROC Curve"
)

plt.plot(
    [0, 100],
    [0, 100],
    linestyle="--",
    label="Random Classifier"
)

plt.xlabel(
    "False Acceptance Rate (%)"
)

plt.ylabel(
    "True Acceptance Rate / TAR (%)"
)

plt.title(
    "ROC Curve - Face Biometric Verification"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    ROC_GRAPH,
    dpi=300
)

plt.close()

print(
    "ROC curve saved to:",
    ROC_GRAPH
)


# ============================================================
# AUC
# ============================================================

# Sort FAR values before numerical integration

sort_index = np.argsort(
    far_values
)

sorted_far = far_values[
    sort_index
]

sorted_tar = tar_values[
    sort_index
]

auc = np.trapz(
    sorted_tar,
    sorted_far
)

print(
    f"AUC: {auc:.6f}"
)

print()


# ============================================================
# FAR / FRR CURVE
# ============================================================

plt.figure(figsize=(10, 6))

plt.plot(
    threshold_values,
    far_values * 100,
    linewidth=2,
    label="FAR"
)

plt.plot(
    threshold_values,
    frr_values * 100,
    linewidth=2,
    label="FRR"
)

plt.axvline(
    CURRENT_THRESHOLD,
    linestyle="--",
    linewidth=2,
    label=(
        f"Current Threshold = "
        f"{CURRENT_THRESHOLD:.2f}"
    )
)

plt.axvline(
    eer_threshold,
    linestyle=":",
    linewidth=2,
    label=(
        f"EER Threshold = "
        f"{eer_threshold:.2f}"
    )
)

plt.xlabel(
    "Authentication Threshold"
)

plt.ylabel(
    "Error Rate (%)"
)

plt.title(
    "FAR and FRR vs Authentication Threshold"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    FAR_FRR_GRAPH,
    dpi=300
)

plt.close()

print(
    "FAR/FRR curve saved to:",
    FAR_FRR_GRAPH
)


# ============================================================
# GENUINE VS IMPOSTOR DISTRIBUTION
# ============================================================

plt.figure(figsize=(10, 6))

plt.hist(
    genuine_scores,
    bins=50,
    alpha=0.6,
    label="Genuine Matches"
)

plt.hist(
    impostor_scores,
    bins=50,
    alpha=0.6,
    label="Impostor Matches"
)

plt.axvline(
    CURRENT_THRESHOLD,
    linestyle="--",
    linewidth=2,
    label=(
        f"Current Threshold = "
        f"{CURRENT_THRESHOLD:.2f}"
    )
)

plt.axvline(
    best_accuracy_threshold,
    linestyle=":",
    linewidth=2,
    label=(
        f"Best Accuracy Threshold = "
        f"{best_accuracy_threshold:.2f}"
    )
)

plt.xlabel(
    "Cosine Similarity"
)

plt.ylabel(
    "Frequency"
)

plt.title(
    "Genuine vs Impostor Similarity Distribution"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    DISTRIBUTION_GRAPH,
    dpi=300
)

plt.close()

print(
    "Similarity distribution saved to:",
    DISTRIBUTION_GRAPH
)


# ============================================================
# F1 SCORE CURVE
# ============================================================

plt.figure(figsize=(10, 6))

plt.plot(
    threshold_values,
    f1_values * 100,
    linewidth=2,
    label="F1 Score"
)

plt.axvline(
    best_f1_threshold,
    linestyle="--",
    linewidth=2,
    label=(
        f"Best F1 Threshold = "
        f"{best_f1_threshold:.2f}"
    )
)

plt.axvline(
    CURRENT_THRESHOLD,
    linestyle=":",
    linewidth=2,
    label=(
        f"Current Threshold = "
        f"{CURRENT_THRESHOLD:.2f}"
    )
)

plt.xlabel(
    "Authentication Threshold"
)

plt.ylabel(
    "F1 Score (%)"
)

plt.title(
    "F1 Score vs Authentication Threshold"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    F1_GRAPH,
    dpi=300
)

plt.close()

print(
    "F1 score curve saved to:",
    F1_GRAPH
)


# ============================================================
# PRECISION / RECALL CURVE
# ============================================================

plt.figure(figsize=(10, 6))

plt.plot(
    threshold_values,
    precision_values * 100,
    linewidth=2,
    label="Precision"
)

plt.plot(
    threshold_values,
    recall_values * 100,
    linewidth=2,
    label="Recall"
)

plt.xlabel(
    "Authentication Threshold"
)

plt.ylabel(
    "Percentage (%)"
)

plt.title(
    "Precision and Recall vs Authentication Threshold"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    PRECISION_RECALL_GRAPH,
    dpi=300
)

plt.close()

print(
    "Precision/Recall curve saved to:",
    PRECISION_RECALL_GRAPH
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

tp = current_result["tp"]
tn = current_result["tn"]
fp = current_result["fp"]
fn = current_result["fn"]

confusion_matrix = np.array(
    [
        [tn, fp],
        [fn, tp]
    ]
)

plt.figure(figsize=(7, 6))

plt.imshow(
    confusion_matrix
)

plt.title(
    f"Confusion Matrix "
    f"(Threshold = {CURRENT_THRESHOLD:.2f})"
)

plt.xlabel(
    "Predicted Class"
)

plt.ylabel(
    "Actual Class"
)

plt.xticks(
    [0, 1],
    ["Impostor", "Genuine"]
)

plt.yticks(
    [0, 1],
    ["Impostor", "Genuine"]
)

for i in range(2):

    for j in range(2):

        plt.text(
            j,
            i,
            str(confusion_matrix[i, j]),
            ha="center",
            va="center",
            fontsize=14
        )

plt.colorbar(
    label="Number of Comparisons"
)

plt.tight_layout()

plt.savefig(
    CONFUSION_GRAPH,
    dpi=300
)

plt.close()

print(
    "Confusion matrix saved to:",
    CONFUSION_GRAPH
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("======================================")
print("VERIFICATION EVALUATION COMPLETED")
print("======================================")

print()

print("Generated files:")

print(
    "1. verification_scores.csv"
)

print(
    "2. verification_results.csv"
)

print(
    "3. roc_curve.png"
)

print(
    "4. far_frr_curve.png"
)

print(
    "5. similarity_distribution.png"
)

print(
    "6. f1_score_curve.png"
)

print(
    "7. precision_recall_curve.png"
)

print(
    "8. confusion_matrix.png"
)

print()

print("IMPORTANT RESULTS")
print("-----------------")

print(
    f"Current Threshold : "
    f"{CURRENT_THRESHOLD:.2f}"
)

print(
    f"Current FAR       : "
    f"{current_result['far'] * 100:.4f}%"
)

print(
    f"Current FRR       : "
    f"{current_result['frr'] * 100:.4f}%"
)

print(
    f"Current TAR       : "
    f"{current_result['tar'] * 100:.4f}%"
)

print(
    f"Current Accuracy  : "
    f"{current_result['accuracy'] * 100:.4f}%"
)

print(
    f"Current Precision : "
    f"{current_result['precision'] * 100:.4f}%"
)

print(
    f"Current Recall    : "
    f"{current_result['recall'] * 100:.4f}%"
)

print(
    f"Current F1        : "
    f"{current_result['f1'] * 100:.4f}%"
)

print(
    f"AUC               : "
    f"{auc:.6f}"
)

print(
    f"EER Threshold     : "
    f"{eer_threshold:.2f}"
)

print(
    f"EER FAR           : "
    f"{eer_far * 100:.4f}%"
)

print(
    f"EER FRR           : "
    f"{eer_frr * 100:.4f}%"
)

print()

print(
    f"Best Accuracy "
    f"Threshold         : "
    f"{best_accuracy_threshold:.2f}"
)

print(
    f"Best Accuracy     : "
    f"{best_accuracy * 100:.4f}%"
)

print(
    f"Best F1 Threshold : "
    f"{best_f1_threshold:.2f}"
)

print(
    f"Best F1 Score     : "
    f"{best_f1 * 100:.4f}%"
)

print()

print("======================================")