import os
import csv
import cv2
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = "low_genuine_scores.csv"

OUTPUT_FILE = "image_quality_analysis.csv"


# ============================================================
# LOAD LOW-SCORE IMAGES
# ============================================================

print("======================================")
print("IMAGE QUALITY DIAGNOSTIC")
print("======================================")
print()

results = []

with open(
    CSV_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        results.append(row)


# ============================================================
# ANALYZE IMAGES
# ============================================================

analysis = []


for item in results:

    subject = item["Subject"]
    image_name = item["Image"]
    image_path = item["Path"]
    similarity = float(item["Similarity"])

    image = cv2.imread(image_path)

    if image is None:

        print(
            "Could not read:",
            image_path
        )

        continue


    # Convert to grayscale

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    # --------------------------------------------------------
    # Brightness
    # --------------------------------------------------------

    brightness = float(
        np.mean(gray)
    )


    # --------------------------------------------------------
    # Contrast
    # --------------------------------------------------------

    contrast = float(
        np.std(gray)
    )


    # --------------------------------------------------------
    # Resolution
    # --------------------------------------------------------

    height, width = gray.shape

    pixels = width * height


    # --------------------------------------------------------
    # Edge strength
    # --------------------------------------------------------

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    edge_ratio = float(
        np.mean(edges > 0)
    ) * 100


    analysis.append(
        {
            "Subject": subject,
            "Image": image_name,
            "Similarity": similarity,
            "Width": width,
            "Height": height,
            "Brightness": brightness,
            "Contrast": contrast,
            "Edge_Ratio": edge_ratio
        }
    )


# ============================================================
# SORT BY SIMILARITY
# ============================================================

analysis.sort(
    key=lambda x: x["Similarity"]
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()

print("======================================")
print("IMAGE QUALITY RESULTS")
print("======================================")
print()

print(
    f"{'Subject':<10}"
    f"{'Image':<15}"
    f"{'Similarity':<12}"
    f"{'Brightness':<12}"
    f"{'Contrast':<12}"
    f"{'Edge %':<10}"
)

print("-" * 75)


for item in analysis:

    print(
        f"{item['Subject']:<10}"
        f"{item['Image']:<15}"
        f"{item['Similarity']:<12.4f}"
        f"{item['Brightness']:<12.2f}"
        f"{item['Contrast']:<12.2f}"
        f"{item['Edge_Ratio']:<10.2f}"
    )


# ============================================================
# SAVE CSV
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = [
        "Subject",
        "Image",
        "Similarity",
        "Width",
        "Height",
        "Brightness",
        "Contrast",
        "Edge_Ratio"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(analysis)


# ============================================================
# COMPLETION
# ============================================================

print()

print("======================================")
print("DIAGNOSTIC COMPLETED")
print("======================================")
print()

print(
    "Saved:",
    OUTPUT_FILE
)

print()

print("======================================")