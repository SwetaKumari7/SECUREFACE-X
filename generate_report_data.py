import os


REPORT_FILE = "report_results.txt"


results = {

    "project_title":
        "Security Enhancement in Deep Learning Based Face Biometric Authentication System",

    "dataset_subjects":
        200,

    "total_images":
        2800,

    "training_images":
        1400,

    "testing_images":
        1400,

    "successful_test_embeddings":
        1387,

    "skipped_test_images":
        13,

    "identification_accuracy":
        99.13,

    "roc_auc":
        99.6805,

    "verification_threshold":
        0.62,

    "far":
        0.1460,

    "frr":
        0.8652,

    "tar":
        99.1348,

    "eer_threshold":
        0.55,

    "eer_far":
        0.6583,

    "eer_frr":
        0.7210,

    "best_raw_accuracy_threshold":
        0.73,

    "best_raw_accuracy":
        99.9816,

    "best_f1_threshold":
        0.73,

    "best_f1":
        98.1528,

    "embedding_dimension":
        512,

    "encryption":
        "AES-256-CBC",

    "integrity":
        "SHA-256",

    "ledger":
        "Local hash-chained tamper-evident ledger",

    "database":
        "SQLite",

    "face_detection":
        "MTCNN",

    "feature_extractor":
        "FaceNet / InceptionResnetV1"
}


with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "SECUREFACE PROJECT RESULTS\n"
    )

    file.write(
        "=" * 60 + "\n\n"
    )


    file.write(
        "PROJECT\n"
    )

    file.write(
        f"{results['project_title']}\n\n"
    )


    file.write(
        "DATASET\n"
    )

    file.write(
        f"Subjects              : "
        f"{results['dataset_subjects']}\n"
    )

    file.write(
        f"Total images          : "
        f"{results['total_images']}\n"
    )

    file.write(
        f"Training images       : "
        f"{results['training_images']}\n"
    )

    file.write(
        f"Testing images        : "
        f"{results['testing_images']}\n"
    )

    file.write(
        f"Successful embeddings  : "
        f"{results['successful_test_embeddings']}\n"
    )

    file.write(
        f"Skipped images         : "
        f"{results['skipped_test_images']}\n\n"
    )


    file.write(
        "MODEL\n"
    )

    file.write(
        f"Face detector         : "
        f"{results['face_detection']}\n"
    )

    file.write(
        f"Feature extractor     : "
        f"{results['feature_extractor']}\n"
    )

    file.write(
        f"Embedding dimension   : "
        f"{results['embedding_dimension']}\n\n"
    )


    file.write(
        "SECURITY\n"
    )

    file.write(
        f"Encryption            : "
        f"{results['encryption']}\n"
    )

    file.write(
        f"Integrity             : "
        f"{results['integrity']}\n"
    )

    file.write(
        f"Ledger                : "
        f"{results['ledger']}\n"
    )

    file.write(
        f"Database              : "
        f"{results['database']}\n\n"
    )


    file.write(
        "AUTHENTICATION RESULTS\n"
    )

    file.write(
        f"Threshold             : "
        f"{results['verification_threshold']:.2f}\n"
    )

    file.write(
        f"Identification Accuracy: "
        f"{results['identification_accuracy']:.2f}%\n"
    )

    file.write(
        f"ROC-AUC               : "
        f"{results['roc_auc']:.4f}%\n"
    )

    file.write(
        f"TAR                   : "
        f"{results['tar']:.4f}%\n"
    )

    file.write(
        f"FAR                   : "
        f"{results['far']:.4f}%\n"
    )

    file.write(
        f"FRR                   : "
        f"{results['frr']:.4f}%\n\n"
    )


    file.write(
        "EER ANALYSIS\n"
    )

    file.write(
        f"EER Threshold         : "
        f"{results['eer_threshold']:.2f}\n"
    )

    file.write(
        f"EER FAR               : "
        f"{results['eer_far']:.4f}%\n"
    )

    file.write(
        f"EER FRR               : "
        f"{results['eer_frr']:.4f}%\n\n"
    )


    file.write(
        "ADDITIONAL ANALYSIS\n"
    )

    file.write(
        f"Best Raw Accuracy Threshold : "
        f"{results['best_raw_accuracy_threshold']:.2f}\n"
    )

    file.write(
        f"Best Raw Accuracy            : "
        f"{results['best_raw_accuracy']:.4f}%\n"
    )

    file.write(
        f"Best F1 Threshold            : "
        f"{results['best_f1_threshold']:.2f}\n"
    )

    file.write(
        f"Best F1 Score                : "
        f"{results['best_f1']:.4f}%\n\n"
    )


    file.write(
        "RECOMMENDED REPORT STATEMENT\n"
    )

    file.write(
        "The proposed face biometric authentication system "
        "achieved an ROC-AUC of 99.68%, demonstrating strong "
        "discrimination between genuine and impostor attempts. "
        "At the selected authentication threshold of 0.62, "
        "the system achieved a TAR of 99.13%, FAR of 0.146%, "
        "and FRR of 0.865%.\n"
    )


print(
    "======================================"
)

print(
    "REPORT DATA GENERATED"
)

print(
    "File:",
    os.path.abspath(REPORT_FILE)
)

print(
    "======================================"
)