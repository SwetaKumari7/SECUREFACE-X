import pickle
import numpy as np


FILE = r"models\face_templates_multi.pkl"


with open(FILE, "rb") as file:
    templates = pickle.load(file)


print("======================================")
print("MULTI-REFERENCE TEMPLATE CHECK")
print("======================================")

print(
    "Registered subjects:",
    len(templates)
)

total_references = 0

for subject_id, data in templates.items():

    embeddings = data["embeddings"]

    total_references += len(embeddings)

    if len(embeddings) > 0:

        print(
            f"Subject {subject_id}: "
            f"{len(embeddings)} references, "
            f"dimension={np.asarray(embeddings[0]).shape}"
        )

    if subject_id == "005":
        break


print()
print(
    "Total reference embeddings:",
    total_references
)

print()
print("======================================")
print("CHECK COMPLETED")
print("======================================")