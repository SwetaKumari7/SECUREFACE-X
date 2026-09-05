import csv
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "dataset_quality_results.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("======================================")
print("QUALITY THRESHOLD ANALYSIS")
print("======================================")
print()

results = []

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        results.append(
            {
                "Subject": row["Subject"],
                "Image": row["Image"],
                "Brightness": float(
                    row["Brightness"]
                ),
                "Contrast": float(
                    row["Contrast"]
                ),
                "Edge_Ratio": float(
                    row["Edge_Ratio"]
                )
            }
        )


total = len(results)


# ============================================================
# CONVERT TO ARRAYS
# ============================================================

brightness = np.array(
    [
        item["Brightness"]
        for item in results
    ]
)

contrast = np.array(
    [
        item["Contrast"]
        for item in results
    ]
)

edge = np.array(
    [
        item["Edge_Ratio"]
        for item in results
    ]
)


# ============================================================
# TEST BRIGHTNESS THRESHOLDS
# ============================================================

print("======================================")
print("BRIGHTNESS THRESHOLDS")
print("======================================")
print()

brightness_thresholds = [
    10,
    15,
    20,
    25,
    30,
    40,
    50,
    60,
    64
]

for threshold in brightness_thresholds:

    rejected = np.sum(
        brightness < threshold
    )

    percentage = (
        rejected / total
    ) * 100

    print(
        f"Brightness < {threshold:>2}: "
        f"{rejected:>4} images "
        f"({percentage:.2f}%)"
    )


# ============================================================
# TEST CONTRAST THRESHOLDS
# ============================================================

print()

print("======================================")
print("CONTRAST THRESHOLDS")
print("======================================")
print()

contrast_thresholds = [
    5,
    7,
    10,
    15,
    20,
    25,
    29
]

for threshold in contrast_thresholds:

    rejected = np.sum(
        contrast < threshold
    )

    percentage = (
        rejected / total
    ) * 100

    print(
        f"Contrast < {threshold:>2}: "
        f"{rejected:>4} images "
        f"({percentage:.2f}%)"
    )


# ============================================================
# TEST EDGE THRESHOLDS
# ============================================================

print()

print("======================================")
print("EDGE THRESHOLDS")
print("======================================")
print()

edge_thresholds = [
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    2.25
]

for threshold in edge_thresholds:

    rejected = np.sum(
        edge < threshold
    )

    percentage = (
        rejected / total
    ) * 100

    print(
        f"Edge < {threshold:>4}: "
        f"{rejected:>4} images "
        f"({percentage:.2f}%)"
    )


# ============================================================
# COMBINED QUALITY RULES
# ============================================================

print()

print("======================================")
print("COMBINED QUALITY RULES")
print("======================================")
print()

rules = [
    (
        "Brightness < 20",
        lambda b, c, e:
        b < 20
    ),

    (
        "Brightness < 30",
        lambda b, c, e:
        b < 30
    ),

    (
        "Brightness < 40",
        lambda b, c, e:
        b < 40
    ),

    (
        "Brightness < 20 OR Contrast < 10",
        lambda b, c, e:
        (b < 20) | (c < 10)
    ),

    (
        "Brightness < 20 OR Edge < 0.5",
        lambda b, c, e:
        (b < 20) | (e < 0.5)
    ),

    (
        "Brightness < 30 OR Contrast < 15",
        lambda b, c, e:
        (b < 30) | (c < 15)
    ),

    (
        "Brightness < 30 OR Edge < 1.0",
        lambda b, c, e:
        (b < 30) | (e < 1.0)
    ),

    (
        "Brightness < 40 OR Contrast < 20",
        lambda b, c, e:
        (b < 40) | (c < 20)
    ),

    (
        "Brightness < 40 OR Edge < 1.0",
        lambda b, c, e:
        (b < 40) | (e < 1.0)
    )
]


for name, rule in rules:

    rejected = np.sum(
        rule(
            brightness,
            contrast,
            edge
        )
    )

    percentage = (
        rejected / total
    ) * 100

    print(
        f"{name:<45} "
        f"{rejected:>4} images "
        f"({percentage:.2f}%)"
    )


# ============================================================
# FINISH
# ============================================================

print()

print("======================================")
print("QUALITY THRESHOLD ANALYSIS COMPLETED")
print("======================================")