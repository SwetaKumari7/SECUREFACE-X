import os
import csv

import cv2
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

TEST_DIR = r"dataset\FEI_DATABASE\TESTING"

OUTPUT_FILE = "dataset_quality_results.csv"


# ============================================================
# START
# ============================================================

print("======================================")
print("FULL DATASET IMAGE QUALITY ANALYSIS")
print("======================================")
print()


# ============================================================
# STORAGE
# ============================================================

results = []

total_images = 0
successful = 0
failed = 0


# ============================================================
# GET SUBJECTS
# ============================================================

subjects = sorted(
    [
        folder
        for folder in os.listdir(TEST_DIR)
        if os.path.isdir(
            os.path.join(TEST_DIR, folder)
        )
    ]
)


print(
    "Subjects:",
    len(subjects)
)

print()


# ============================================================
# PROCESS ALL TESTING IMAGES
# ============================================================

for subject in subjects:

    subject_path = os.path.join(
        TEST_DIR,
        subject
    )

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


        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        image = cv2.imread(image_path)


        if image is None:

            failed += 1

            continue


        # ----------------------------------------------------
        # Convert to grayscale
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        # ----------------------------------------------------
        # Image dimensions
        # ----------------------------------------------------

        height, width = gray.shape


        # ----------------------------------------------------
        # Brightness
        # ----------------------------------------------------

        brightness = float(
            np.mean(gray)
        )


        # ----------------------------------------------------
        # Contrast
        # ----------------------------------------------------

        contrast = float(
            np.std(gray)
        )


        # ----------------------------------------------------
        # Edge information
        # ----------------------------------------------------

        edges = cv2.Canny(
            gray,
            50,
            150
        )


        edge_ratio = float(
            np.mean(edges > 0)
        ) * 100


        # ----------------------------------------------------
        # Save result
        # ----------------------------------------------------

        results.append(
            {
                "Subject": subject,
                "Image": image_file,
                "Width": width,
                "Height": height,
                "Brightness": brightness,
                "Contrast": contrast,
                "Edge_Ratio": edge_ratio
            }
        )


        successful += 1


# ============================================================
# CONVERT TO NUMPY ARRAYS
# ============================================================

brightness_values = np.array(
    [
        item["Brightness"]
        for item in results
    ]
)


contrast_values = np.array(
    [
        item["Contrast"]
        for item in results
    ]
)


edge_values = np.array(
    [
        item["Edge_Ratio"]
        for item in results
    ]
)


# ============================================================
# DISPLAY BASIC STATISTICS
# ============================================================

print("======================================")
print("DATASET SUMMARY")
print("======================================")
print()

print(
    "Total images:",
    total_images
)

print(
    "Successfully analyzed:",
    successful
)

print(
    "Failed:",
    failed
)

print()


# ============================================================
# BRIGHTNESS STATISTICS
# ============================================================

print("======================================")
print("BRIGHTNESS STATISTICS")
print("======================================")
print()

print(
    f"Minimum : {np.min(brightness_values):.2f}"
)

print(
    f"Maximum : {np.max(brightness_values):.2f}"
)

print(
    f"Mean    : {np.mean(brightness_values):.2f}"
)

print(
    f"Median  : {np.median(brightness_values):.2f}"
)

print(
    f"10%     : {np.percentile(brightness_values, 10):.2f}"
)

print(
    f"25%     : {np.percentile(brightness_values, 25):.2f}"
)

print(
    f"75%     : {np.percentile(brightness_values, 75):.2f}"
)

print(
    f"90%     : {np.percentile(brightness_values, 90):.2f}"
)

print()


# ============================================================
# CONTRAST STATISTICS
# ============================================================

print("======================================")
print("CONTRAST STATISTICS")
print("======================================")
print()

print(
    f"Minimum : {np.min(contrast_values):.2f}"
)

print(
    f"Maximum : {np.max(contrast_values):.2f}"
)

print(
    f"Mean    : {np.mean(contrast_values):.2f}"
)

print(
    f"Median  : {np.median(contrast_values):.2f}"
)

print(
    f"10%     : {np.percentile(contrast_values, 10):.2f}"
)

print(
    f"25%     : {np.percentile(contrast_values, 25):.2f}"
)

print(
    f"75%     : {np.percentile(contrast_values, 75):.2f}"
)

print(
    f"90%     : {np.percentile(contrast_values, 90):.2f}"
)

print()


# ============================================================
# EDGE STATISTICS
# ============================================================

print("======================================")
print("EDGE INFORMATION STATISTICS")
print("======================================")
print()

print(
    f"Minimum : {np.min(edge_values):.2f}%"
)

print(
    f"Maximum : {np.max(edge_values):.2f}%"
)

print(
    f"Mean    : {np.mean(edge_values):.2f}%"
)

print(
    f"Median  : {np.median(edge_values):.2f}%"
)

print(
    f"10%     : {np.percentile(edge_values, 10):.2f}%"
)

print(
    f"25%     : {np.percentile(edge_values, 25):.2f}%"
)

print(
    f"75%     : {np.percentile(edge_values, 75):.2f}%"
)

print(
    f"90%     : {np.percentile(edge_values, 90):.2f}%"
)

print()


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

    writer.writerows(results)


# ============================================================
# COMPLETION
# ============================================================

print("======================================")
print("ANALYSIS COMPLETED")
print("======================================")
print()

print(
    "Saved:",
    OUTPUT_FILE
)

print()

print("======================================")