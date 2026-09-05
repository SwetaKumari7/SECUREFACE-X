import csv
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

SCORES_FILE = "verification_scores.csv"
CURRENT_THRESHOLD = 0.62


# ============================================================
# LOAD SCORES
# ============================================================

genuine_scores = []
impostor_scores = []

print("======================================")
print("ROC / AUC EVALUATION")
print("======================================")
print()

print("Loading:", SCORES_FILE)

with open(
    SCORES_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        score = float(row["Score"])
        label = int(row["Label"])

        if label == 1:
            genuine_scores.append(score)
        else:
            impostor_scores.append(score)


genuine_scores = np.array(
    genuine_scores,
    dtype=float
)

impostor_scores = np.array(
    impostor_scores,
    dtype=float
)


# ============================================================
# CREATE PROPER ROC POINTS
# ============================================================

# Use all unique scores as thresholds.
# Higher similarity means stronger evidence for genuine.

all_scores = np.concatenate(
    [
        genuine_scores,
        impostor_scores
    ]
)

thresholds = np.unique(
    all_scores
)

# Add boundaries
thresholds = np.concatenate(
    [
        [np.max(all_scores) + 1],
        thresholds,
        [np.min(all_scores) - 1]
    ]
)

far_values = []
tar_values = []


for threshold in thresholds:

    true_positive = np.sum(
        genuine_scores >= threshold
    )

    false_positive = np.sum(
        impostor_scores >= threshold
    )

    tar = (
        true_positive
        / len(genuine_scores)
    )

    far = (
        false_positive
        / len(impostor_scores)
    )

    tar_values.append(tar)
    far_values.append(far)


far_values = np.array(far_values)
tar_values = np.array(tar_values)


# ============================================================
# SORT ROC POINTS
# ============================================================

sort_index = np.argsort(
    far_values
)

far_sorted = far_values[
    sort_index
]

tar_sorted = tar_values[
    sort_index
]


# ============================================================
# REMOVE DUPLICATE FAR VALUES
# ============================================================

unique_far, unique_indices = np.unique(
    far_sorted,
    return_index=True
)

unique_tar = tar_sorted[
    unique_indices
]


# ============================================================
# CALCULATE AUC
# ============================================================

auc = np.trapz(
    unique_tar,
    unique_far
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("======================================")
print("ROC RESULTS")
print("======================================")

print()

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
    f"Correct ROC AUC: {auc:.6f}"
)

print(
    f"ROC AUC (%): {auc * 100:.4f}%"
)


# ============================================================
# CURRENT THRESHOLD
# ============================================================

tp = np.sum(
    genuine_scores >= CURRENT_THRESHOLD
)

fn = np.sum(
    genuine_scores < CURRENT_THRESHOLD
)

fp = np.sum(
    impostor_scores >= CURRENT_THRESHOLD
)

tn = np.sum(
    impostor_scores < CURRENT_THRESHOLD
)

far = fp / len(impostor_scores)

tar = tp / len(genuine_scores)

frr = fn / len(genuine_scores)


print()
print("======================================")
print(
    f"THRESHOLD {CURRENT_THRESHOLD:.2f}"
)
print("======================================")

print(
    f"FAR : {far * 100:.4f}%"
)

print(
    f"FRR : {frr * 100:.4f}%"
)

print(
    f"TAR : {tar * 100:.4f}%"
)

print()


# ============================================================
# SAVE CORRECT ROC GRAPH
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    unique_far * 100,
    unique_tar * 100,
    linewidth=2,
    label=f"ROC Curve (AUC = {auc:.4f})"
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
    "True Acceptance Rate (%)"
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
    "roc_curve_corrected.png",
    dpi=300
)

plt.close()


print(
    "Corrected ROC graph saved to:"
)

print(
    "roc_curve_corrected.png"
)

print()

print("======================================")
print("AUC CALCULATION COMPLETED")
print("======================================")