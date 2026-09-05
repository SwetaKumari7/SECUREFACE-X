import csv
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

SCORES_FILE = "verification_scores.csv"

THRESHOLD = 0.62


# ============================================================
# LOAD SCORES
# ============================================================

genuine_scores = []
impostor_scores = []

print("======================================")
print("COMPLETE BIOMETRIC EVALUATION")
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
# BASIC STATISTICS
# ============================================================

print()
print("======================================")
print("SCORE STATISTICS")
print("======================================")

print()

print("Genuine comparisons:",
      len(genuine_scores))

print("Impostor comparisons:",
      len(impostor_scores))

print()

print("GENUINE")

print(
    "Minimum:",
    f"{np.min(genuine_scores):.4f}"
)

print(
    "Maximum:",
    f"{np.max(genuine_scores):.4f}"
)

print(
    "Mean:",
    f"{np.mean(genuine_scores):.4f}"
)

print(
    "Median:",
    f"{np.median(genuine_scores):.4f}"
)

print()

print("IMPOSTOR")

print(
    "Minimum:",
    f"{np.min(impostor_scores):.4f}"
)

print(
    "Maximum:",
    f"{np.max(impostor_scores):.4f}"
)

print(
    "Mean:",
    f"{np.mean(impostor_scores):.4f}"
)

print(
    "Median:",
    f"{np.median(impostor_scores):.4f}"
)


# ============================================================
# THRESHOLD METRICS
# ============================================================

tp = np.sum(
    genuine_scores >= THRESHOLD
)

fn = np.sum(
    genuine_scores < THRESHOLD
)

fp = np.sum(
    impostor_scores >= THRESHOLD
)

tn = np.sum(
    impostor_scores < THRESHOLD
)

far = fp / len(impostor_scores)

frr = fn / len(genuine_scores)

tar = tp / len(genuine_scores)

accuracy = (
    tp + tn
) / (
    tp
    + tn
    + fp
    + fn
)

precision = (
    tp / (tp + fp)
    if (tp + fp) > 0
    else 0
)

recall = (
    tp / (tp + fn)
    if (tp + fn) > 0
    else 0
)

f1 = (
    2 * precision * recall
    / (precision + recall)
    if (precision + recall) > 0
    else 0
)


# ============================================================
# DISPLAY METRICS
# ============================================================

print()
print("======================================")
print(
    f"METRICS AT THRESHOLD {THRESHOLD:.2f}"
)
print("======================================")

print(
    f"FAR       : {far * 100:.4f}%"
)

print(
    f"FRR       : {frr * 100:.4f}%"
)

print(
    f"TAR       : {tar * 100:.4f}%"
)

print(
    f"Accuracy  : {accuracy * 100:.4f}%"
)

print(
    f"Precision : {precision * 100:.4f}%"
)

print(
    f"Recall    : {recall * 100:.4f}%"
)

print(
    f"F1 Score  : {f1 * 100:.4f}%"
)

print()

print("TP:", tp)
print("TN:", tn)
print("FP:", fp)
print("FN:", fn)


# ============================================================
# THRESHOLD SWEEP
# ============================================================

thresholds = np.arange(
    0.30,
    0.96,
    0.01
)

far_values = []
frr_values = []
tar_values = []
accuracy_values = []
precision_values = []
recall_values = []
f1_values = []


for threshold in thresholds:

    tp_temp = np.sum(
        genuine_scores >= threshold
    )

    fn_temp = np.sum(
        genuine_scores < threshold
    )

    fp_temp = np.sum(
        impostor_scores >= threshold
    )

    tn_temp = np.sum(
        impostor_scores < threshold
    )

    far_temp = (
        fp_temp
        / len(impostor_scores)
    )

    frr_temp = (
        fn_temp
        / len(genuine_scores)
    )

    tar_temp = (
        tp_temp
        / len(genuine_scores)
    )

    accuracy_temp = (
        tp_temp + tn_temp
    ) / (
        tp_temp
        + tn_temp
        + fp_temp
        + fn_temp
    )

    precision_temp = (
        tp_temp
        / (tp_temp + fp_temp)
        if (tp_temp + fp_temp) > 0
        else 0
    )

    recall_temp = (
        tp_temp
        / (tp_temp + fn_temp)
        if (tp_temp + fn_temp) > 0
        else 0
    )

    f1_temp = (
        2
        * precision_temp
        * recall_temp
        / (
            precision_temp
            + recall_temp
        )
        if (
            precision_temp
            + recall_temp
        ) > 0
        else 0
    )

    far_values.append(far_temp)
    frr_values.append(frr_temp)
    tar_values.append(tar_temp)
    accuracy_values.append(
        accuracy_temp
    )
    precision_values.append(
        precision_temp
    )
    recall_values.append(
        recall_temp
    )
    f1_values.append(
        f1_temp
    )


far_values = np.array(far_values)
frr_values = np.array(frr_values)
tar_values = np.array(tar_values)
accuracy_values = np.array(
    accuracy_values
)
precision_values = np.array(
    precision_values
)
recall_values = np.array(
    recall_values
)
f1_values = np.array(
    f1_values
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

eer_threshold = thresholds[
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
    thresholds[
        best_accuracy_index
    ]
)

best_accuracy = (
    accuracy_values[
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
    thresholds[
        best_f1_index
    ]
)

best_f1 = (
    f1_values[
        best_f1_index
    ]
)


# ============================================================
# ROC CURVE
# ============================================================

# FAR = False Positive Rate
# TAR = True Positive Rate

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


plt.figure(
    figsize=(10, 6)
)

plt.plot(
    sorted_far * 100,
    sorted_tar * 100,
    linewidth=2,
    label=f"ROC (AUC = {auc:.4f})"
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
    "roc_curve.png",
    dpi=300
)

plt.close()


# ============================================================
# FAR / FRR GRAPH
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    thresholds,
    far_values * 100,
    label="FAR"
)

plt.plot(
    thresholds,
    frr_values * 100,
    label="FRR"
)

plt.axvline(
    THRESHOLD,
    linestyle="--",
    label=f"Current Threshold = {THRESHOLD:.2f}"
)

plt.axvline(
    eer_threshold,
    linestyle=":",
    label=f"EER Threshold = {eer_threshold:.2f}"
)

plt.xlabel(
    "Threshold"
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
    "far_frr_curve.png",
    dpi=300
)

plt.close()


# ============================================================
# SCORE DISTRIBUTION
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    genuine_scores,
    bins=50,
    alpha=0.6,
    label="Genuine"
)

plt.hist(
    impostor_scores,
    bins=50,
    alpha=0.6,
    label="Impostor"
)

plt.axvline(
    THRESHOLD,
    linestyle="--",
    linewidth=2,
    label=f"Threshold = {THRESHOLD:.2f}"
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
    "similarity_distribution.png",
    dpi=300
)

plt.close()


# ============================================================
# F1 CURVE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    thresholds,
    f1_values * 100,
    label="F1 Score"
)

plt.axvline(
    best_f1_threshold,
    linestyle="--",
    label=f"Best F1 = {best_f1_threshold:.2f}"
)

plt.xlabel(
    "Threshold"
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
    "f1_score_curve.png",
    dpi=300
)

plt.close()


# ============================================================
# PRECISION / RECALL CURVE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    thresholds,
    precision_values * 100,
    label="Precision"
)

plt.plot(
    thresholds,
    recall_values * 100,
    label="Recall"
)

plt.xlabel(
    "Threshold"
)

plt.ylabel(
    "Percentage (%)"
)

plt.title(
    "Precision and Recall vs Threshold"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "precision_recall_curve.png",
    dpi=300
)

plt.close()


# ============================================================
# CONFUSION MATRIX
# ============================================================

matrix = np.array(
    [
        [tn, fp],
        [fn, tp]
    ]
)

plt.figure(
    figsize=(7, 6)
)

plt.imshow(
    matrix
)

plt.title(
    f"Confusion Matrix "
    f"(Threshold = {THRESHOLD:.2f})"
)

plt.xlabel(
    "Predicted"
)

plt.ylabel(
    "Actual"
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
            str(matrix[i, j]),
            ha="center",
            va="center",
            fontsize=14
        )

plt.colorbar(
    label="Count"
)

plt.tight_layout()

plt.savefig(
    "confusion_matrix.png",
    dpi=300
)

plt.close()


# ============================================================
# FINAL RESULTS
# ============================================================

print()
print("======================================")
print("FINAL COMPLETE EVALUATION")
print("======================================")

print()

print(
    f"AUC                : {auc:.6f}"
)

print(
    f"EER Threshold      : {eer_threshold:.2f}"
)

print(
    f"EER FAR            : {eer_far * 100:.4f}%"
)

print(
    f"EER FRR            : {eer_frr * 100:.4f}%"
)

print()

print(
    f"Best Accuracy Thr. : "
    f"{best_accuracy_threshold:.2f}"
)

print(
    f"Best Accuracy      : "
    f"{best_accuracy * 100:.4f}%"
)

print()

print(
    f"Best F1 Threshold  : "
    f"{best_f1_threshold:.2f}"
)

print(
    f"Best F1 Score      : "
    f"{best_f1 * 100:.4f}%"
)

print()

print("Generated graphs:")

print("roc_curve.png")
print("far_frr_curve.png")
print("similarity_distribution.png")
print("f1_score_curve.png")
print("precision_recall_curve.png")
print("confusion_matrix.png")

print()

print("======================================")
print("EVALUATION COMPLETE")
print("======================================")