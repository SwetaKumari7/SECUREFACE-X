import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# LOAD VERIFICATION RESULTS
# ==========================================

data = pd.read_csv("verification_results.csv")


# ==========================================
# CREATE FAR / FRR GRAPH
# ==========================================

plt.figure(figsize=(10, 6))


plt.plot(
    data["Threshold"],
    data["FAR"] * 100,
    label="FAR"
)


plt.plot(
    data["Threshold"],
    data["FRR"] * 100,
    label="FRR"
)


# Best threshold from your evaluation
best_threshold = 0.73


plt.axvline(
    best_threshold,
    linestyle="--",
    linewidth=2,
    label="Best Threshold = 0.73"
)


plt.xlabel("Threshold")

plt.ylabel("Error Rate (%)")

plt.title(
    "FAR and FRR vs Authentication Threshold"
)

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()


# ==========================================
# SAVE GRAPH
# ==========================================

plt.savefig(
    "far_frr_curve.png",
    dpi=300
)

plt.close()


print("======================================")
print("GRAPH CREATED SUCCESSFULLY")
print("======================================")
print()
print("File created:")
print("far_frr_curve.png")
print()
print("======================================")