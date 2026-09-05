# SECUREFACE X

## Security-Enhanced Deep Learning Based Face Biometric Authentication System

SECUREFACE X is a security-focused biometric authentication system that combines deep-learning-based face recognition with cybersecurity mechanisms such as encrypted biometric templates, integrity verification, tamper detection, authentication-abuse detection, temporary account lockout, security-event logging, and SOC-style security monitoring.

Unlike a conventional face-recognition application that only checks whether a face matches a registered identity, SECUREFACE X treats biometric authentication as a complete security system.

## Core Features

- MTCNN face detection
- InceptionResNetV1 / FaceNet embeddings
- Pretrained VGGFace2 model
- 512-dimensional facial embeddings
- Subject-level biometric templates
- Cosine similarity verification
- Authentication threshold: 0.62
- Image-quality analysis
- AES-256-CBC encrypted biometric templates
- SHA-256 integrity verification
- Local hash-chained tamper-evident ledger
- Authentication-abuse detection
- Three-attempt temporary lockout
- Two-minute lockout duration
- SQLite security-event logging
- SOC-style security dashboard
- Dynamic threat monitoring
- Security audit log
- Controlled biometric Attack Lab
- ROC, FAR, FRR, TAR and F1 evaluation

## System Architecture

```text
Input Face Image
       |
       v
Face Detection (MTCNN)
       |
       v
Image Quality Analysis
       |
       v
InceptionResNetV1
       |
       v
512-D Face Embedding
       |
       v
Subject-Level Template
       |
       v
AES-256-CBC Protection
       |
       +------------------+
       |                  |
       v                  v
SHA-256 Integrity   Hash-Chained Ledger
       |                  |
       +--------+---------+
                |
                v
        Cosine Similarity
                |
          +-----+-----+
          |           |
          v           v
       VERIFIED    REJECTED
                      |
                      v
             Failed Attempt Monitor
                      |
                      v
               Temporary Lockout
                      |
                      v
             Security Event Logging
                      |
                      v
                SOC Dashboard
```

## Problem Statement

Traditional face-recognition systems primarily concentrate on recognition accuracy. A secure biometric system must also protect stored biometric templates, detect unauthorized modification, limit repeated authentication abuse, record security events, and provide monitoring and auditability.

SECUREFACE X extends face recognition with these defensive security controls.

## Objectives

1. Detect faces from input images.
2. Generate deep-learning facial embeddings.
3. Create subject-level biometric templates.
4. Encrypt stored templates using AES-256-CBC.
5. Detect template modification using SHA-256.
6. Maintain a local hash-chained tamper-evident ledger.
7. Authenticate users using cosine similarity.
8. Perform basic image-quality analysis.
9. Detect repeated authentication failures.
10. Temporarily lock suspicious identities.
11. Record security events.
12. Provide a SOC-style monitoring dashboard.
13. Provide a controlled security Attack Lab.
14. Evaluate biometric performance using standard metrics.

## Machine Learning Pipeline

```text
FEI Face Image
      |
      v
MTCNN
      |
      v
Detected Face
      |
      v
InceptionResNetV1
      |
      v
512-D Embedding
      |
      v
Normalization
      |
      v
Subject-Level Template
      |
      v
Cosine Similarity
      |
      v
Authentication Decision
```

### Face Detection

The system uses MTCNN (Multi-task Cascaded Convolutional Networks) to detect and extract faces before embedding generation.

### Face Embedding

InceptionResNetV1 is used through `facenet-pytorch` with pretrained VGGFace2 weights. Each detected face produces a 512-dimensional embedding.

**Important:** The FaceNet/InceptionResNetV1 model was not trained from scratch on the FEI dataset. The pretrained model is used as the feature extractor, while the FEI dataset is used for biometric template generation and system evaluation.

## Biometric Template Generation

Training images are processed to create embeddings for each subject. Embeddings belonging to the same subject are combined into a subject-level biometric template.

```text
Subject
  |
  +-- Image 1 -> Embedding
  +-- Image 2 -> Embedding
  +-- Image 3 -> Embedding
  +-- ...
  |
  v
Subject-Level Template
```

## Authentication

The system compares the submitted face embedding with the registered template using cosine similarity.

Current threshold:

```text
0.62
```

Decision rule:

```text
Similarity >= 0.62  -> VERIFIED
Similarity <  0.62  -> REJECTED
```

## Image Quality Analysis

The system performs basic quality checks using characteristics including:

- Resolution
- Brightness
- Contrast
- Edge information

Poor-quality images can negatively affect face detection and authentication reliability.

## Biometric Template Security

Stored biometric templates are protected using multiple security layers:

```text
Biometric Template
       |
       v
AES-256-CBC Encryption
       |
       v
Encrypted Template
       |
       +---- SHA-256 Integrity
       |
       +---- Hash-Chained Ledger
```

| Mechanism | Purpose |
|---|---|
| AES-256-CBC | Confidentiality |
| SHA-256 | Integrity detection |
| Hash-chained ledger | Tamper-evident record |
| Security guard | Authentication-abuse protection |
| SQLite | Auditability and event storage |

### AES-256-CBC

AES-256-CBC protects the stored biometric template from unauthorized disclosure.

The encryption key is stored locally and must never be uploaded to a public GitHub repository.

### SHA-256

SHA-256 is used to detect modification of the encrypted template.

```text
Encrypted Template
       |
       v
    SHA-256
       |
       v
Hash Comparison
       |
   +---+---+
   |       |
   v       v
MATCH   MISMATCH
   |       |
   v       v
PASS    FAILURE
```

### Hash-Chained Ledger

The project implements a local hash-chained tamper-evident ledger.

```text
Block 0
   |
   v
Block 1
   |
   v
Block 2
   |
   v
Block 3
```

This is **not** a decentralized public blockchain. It is a local integrity mechanism used to demonstrate tamper evidence.

## Authentication Abuse Detection

The system tracks repeated failed authentication attempts.

Current configuration:

```text
Maximum Failed Attempts: 3
Lockout Duration: 2 minutes
```

Example:

```text
Attempt 1 -> FAILED
Attempt 2 -> FAILED
Attempt 3 -> FAILED
              |
              v
     AUTHENTICATION ABUSE
              |
              v
       TEMPORARY LOCKOUT
```

## Security Event Logging

Security events are stored in SQLite.

Examples include:

- Authentication abuse
- Repeated failed authentication
- Temporary lockout
- Authentication blocked
- Template integrity failures

Events can contain:

```text
Subject ID
Attack Type
Severity
Source
Action Taken
Timestamp
```

## SOC Dashboard

The web dashboard provides visibility into:

- Registered subjects
- Verification attempts
- Security events
- High-severity events
- Blocked actions
- Current threat level
- ROC-AUC
- F1 score
- Template integrity
- Security audit records

Threat levels are dynamically represented as:

```text
LOW       -> 0 high-severity events
ELEVATED  -> 1-2 high-severity events
CRITICAL  -> 3 or more high-severity events
```

## Biometric Attack Lab

The controlled Attack Lab provides three defensive tests:

1. Template Tampering
2. Integrity Validation
3. Authentication Abuse

### Template Tampering

A temporary modified copy of the encrypted template is tested. The real template is restored after the test.

```text
Encrypted Template
       |
       v
Temporary Modification
       |
       v
SHA-256 Mismatch
       |
       v
Tampering Detected
       |
       v
Authentication Blocked
```

### Integrity Validation

The system validates the protected template against its expected integrity information and the local hash-chained ledger.

### Authentication Abuse

Repeated failed attempts are simulated to demonstrate the three-attempt lockout mechanism and security-event creation.

## Database

SECUREFACE X uses SQLite.

Main tables include:

- `users`
- `verification_logs`
- `security_events`
- `authentication_security`

### users

Stores registered subject information such as subject ID, registration date and status.

### verification_logs

Stores verification information including similarity score, result, image-quality values, security status and timestamp.

### security_events

Stores security incidents such as authentication abuse, tampering and blocked authentication.

### authentication_security

Stores failed-attempt and lockout state.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| Deep Learning | PyTorch |
| Face Recognition | InceptionResNetV1 / FaceNet |
| Pretrained Weights | VGGFace2 |
| Face Detection | MTCNN |
| Image Processing | Pillow |
| Numerical Processing | NumPy |
| Evaluation | scikit-learn |
| Data Analysis | Pandas |
| Visualization | Matplotlib |
| Cryptography | cryptography |
| Encryption | AES-256-CBC |
| Hashing | SHA-256 |
| Web Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Templating | Jinja2 |
| Database | SQLite |

## Project Structure

```text
SECUREFACE_X/
|
|-- app.py
|-- face_engine.py
|-- security.py
|-- security_guard.py
|-- database.py
|-- blockchain.py
|-- train.py
|
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- templates/
|   |-- dashboard.html
|   `-- ...
|
|-- models/
|   `-- local protected resources
|
|-- data/
|   `-- local security resources
|
`-- dataset/
    `-- FEI_DATABASE/
```

Sensitive runtime files should remain local.

## Dataset

The project uses the FEI Face Database for biometric evaluation.

Evaluated dataset:

```text
Subjects:        200
Training Images: 1400
Testing Images:  1400
Total Images:    2800
```

The dataset is not included in this repository.

Expected local structure:

```text
dataset/
`-- FEI_DATABASE/
    |-- TRAINING/
    |   |-- 001/
    |   |-- 002/
    |   |-- ...
    |   `-- 200/
    |
    `-- TESTING/
        |-- 001/
        |-- 002/
        |-- ...
        `-- 200/
```

## Evaluation Results

The system was evaluated using the FEI testing images.

### Identification

```text
Total Test Images   : 1400
Tested Images       : 1387
Skipped Images      : 13
Correct Predictions : 1375
```

Identification accuracy:

```text
99.13%
```

### Verification Performance

At the selected threshold of `0.62`:

```text
ROC-AUC : 99.68%
TAR     : 99.13%
FAR     : 0.146%
FRR     : 0.865%
F1      : 86.89%
```

### Evaluation Summary

| Metric | Result |
|---|---:|
| Registered Subjects | 200 |
| Total Test Images | 1,400 |
| Tested Images | 1,387 |
| Skipped Images | 13 |
| Correct Predictions | 1,375 |
| Identification Accuracy | **99.13%** |
| ROC-AUC | **99.68%** |
| TAR | **99.13%** |
| FAR | **0.146%** |
| FRR | **0.865%** |
| F1 Score @ 0.62 | **86.89%** |
| Authentication Threshold | **0.62** |

### Metric Interpretation

**Identification Accuracy** measures the percentage of evaluated test images correctly identified.

**ROC-AUC** measures how well genuine and impostor comparisons are separated across thresholds.

**TAR (True Acceptance Rate)** measures correctly accepted genuine attempts.

**FAR (False Acceptance Rate)** measures impostor attempts that are incorrectly accepted.

**FRR (False Rejection Rate)** measures genuine attempts that are incorrectly rejected.

The identification accuracy and ROC-AUC are different metrics and should not be presented as the same value or as the training accuracy of the pretrained FaceNet model.

## Authentication vs Template Integrity

These are deliberately separate security checks.

### Authentication

Question:

> Does the submitted face belong to the claimed identity?

Determined using face embeddings and cosine similarity.

### Integrity

Question:

> Has the protected biometric template been modified?

Determined using SHA-256 and the hash-chained ledger.

Therefore this is a valid outcome:

```text
Template Integrity -> PASSED
Face Similarity    -> BELOW THRESHOLD
Authentication     -> REJECTED
```

The template can be intact while the submitted face is still rejected.

## Recommended Demonstration

```text
1. Start the Flask application
2. Perform genuine verification
3. Perform a rejected verification
4. Demonstrate repeated failed attempts
5. Show temporary lockout
6. Open the SOC dashboard
7. Open Attack Lab
8. Run template tampering test
9. Show integrity failure
10. Run integrity validation
11. Show integrity passed
12. Run authentication-abuse test
13. Show lockout/security event
14. Review the audit log
```

## Installation

### Requirements

Recommended environment:

```text
Python 3.11
```

### Create Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Dataset Setup

Place the FEI dataset locally:

```text
dataset/
`-- FEI_DATABASE/
    |-- TRAINING/
    `-- TESTING/
```

Do not commit the dataset to GitHub.

## Generate Biometric Templates

Run:

```bash
python train.py
```

This processes the training images and creates subject-level biometric templates.

Keep generated biometric resources local.

## Initialize Database

Run:

```bash
python database.py
```

## Run the Application

Start Flask:

```bash
python app.py
```

Main application:

```text
http://127.0.0.1:5000/
```

Dashboard:

```text
http://127.0.0.1:5000/dashboard
```

Attack Lab:

```text
http://127.0.0.1:5000/attack-lab
```


## Security Design

SECUREFACE X follows a layered security architecture:

```text
Face Detection
      |
Image Quality
      |
Deep-Learning Embedding
      |
Biometric Verification
      |
AES Template Protection
      |
SHA-256 Integrity
      |
Hash-Chained Ledger
      |
Authentication Abuse Detection
      |
Temporary Lockout
      |
Security Event Logging
      |
SOC Monitoring
```

## CIA Perspective

### Confidentiality

AES-256-CBC protects stored biometric templates from unauthorized disclosure.

### Integrity

SHA-256 and the local hash-chained ledger help detect unauthorized modification.

### Authentication Security

Face verification, failed-attempt monitoring and temporary lockout provide defensive authentication controls.

## Limitations

### No Dedicated Liveness Detection

The current system does not implement a dedicated liveness-detection or presentation-attack-detection model. It should therefore not be described as a complete anti-spoofing system.

### Pretrained Model

The face-recognition network is pretrained and is not trained from scratch on the FEI dataset.

### Local Ledger

The hash-chained ledger is a local tamper-evident mechanism, not a decentralized blockchain network.

### Prototype Deployment

The Flask development server is intended for academic and research demonstration rather than production deployment.

### Dataset Dependence

Performance depends on dataset characteristics, lighting, pose, image quality, face-detection success and the experimental configuration.

### Cryptographic Architecture

The current implementation uses AES-256-CBC with a separate SHA-256 integrity mechanism. A production implementation should use authenticated encryption such as AES-GCM or an equivalent authenticated cryptographic design, together with secure key management.

## Future Enhancements

- Dedicated liveness detection
- Presentation-attack detection
- Anti-spoofing models
- Multi-factor authentication
- Hardware-backed key storage
- AES-GCM authenticated encryption
- Secure key-management infrastructure
- Role-based access control
- Production WSGI deployment
- Secure remote database
- Privacy-preserving biometric templates
- Centralized SIEM integration
- Risk-based authentication
- Behavioral anomaly detection
- Continuous security monitoring
- Advanced biometric template protection
- Secure cloud deployment
- Hardware security modules

## Project Significance

SECUREFACE X demonstrates the integration of:

```text
Artificial Intelligence
        +
Computer Vision
        +
Biometrics
        +
Cybersecurity
        +
Web Security Monitoring
```

The project treats biometric authentication as a security system rather than only a recognition model.

It addresses:

- Face detection
- Identity verification
- Template confidentiality
- Template integrity
- Authentication abuse
- Defensive response
- Security-event logging
- Auditability
- Security monitoring

## Project Status

```text
Face Detection                    ✓
Face Embedding                    ✓
Biometric Template Generation    ✓
Biometric Authentication          ✓
Cosine Similarity                 ✓
Image Quality Analysis            ✓
AES-256-CBC Protection            ✓
SHA-256 Integrity                 ✓
Tamper Detection                  ✓
Hash-Chained Ledger               ✓
Authentication Abuse Detection    ✓
Temporary Lockout                 ✓
Security Event Logging             ✓
SQLite Database                   ✓
SOC Dashboard                     ✓
Dynamic Threat Monitoring         ✓
Security Audit Log                ✓
Attack Lab                        ✓
ROC Evaluation                    ✓
ROC-AUC Evaluation                ✓
FAR/FRR Evaluation                ✓
TAR Evaluation                    ✓
F1 Evaluation                     ✓
Precision-Recall Evaluation       ✓
Confusion Matrix                  ✓
```

## Final Performance

```text
Registered Subjects      : 200
Total Test Images        : 1,400
Tested Images            : 1,387
Correct Predictions      : 1,375

Identification Accuracy  : 99.13%

ROC-AUC                   : 99.68%
TAR                       : 99.13%
FAR                       : 0.146%
FRR                       : 0.865%
F1 Score @ 0.62           : 86.89%

Authentication Threshold  : 0.62

Maximum Failed Attempts  : 3
Lockout Duration          : 2 minutes
```

## Conclusion

SECUREFACE X demonstrates a layered approach to deep-learning-based face biometric authentication by combining biometric recognition with cybersecurity controls.

The system integrates:

```text
Deep Learning
+
Computer Vision
+
Face Biometrics
+
Biometric Template Protection
+
AES Encryption
+
SHA-256 Integrity
+
Tamper-Evident Ledger
+
Authentication Monitoring
+
Temporary Lockout
+
Security Event Logging
+
SOC Monitoring
+
Controlled Attack Testing
+
Biometric Evaluation
```

Under the evaluated experimental configuration, the system achieved:

```text
Identification Accuracy : 99.13%
ROC-AUC                  : 99.68%
TAR                      : 99.13%
FAR                      : 0.146%
FRR                      : 0.865%
F1 Score @ 0.62         : 86.89%
```

The project demonstrates that a secure biometric authentication system requires more than recognition performance. It must also protect biometric templates, detect integrity violations, control authentication abuse, log security events and provide security monitoring.

## Author

**Sweta Kumari**

B.Tech — Information Technology

Project: **SECUREFACE X**

Domains:

- Deep Learning
- Computer Vision
- Biometrics
- Cybersecurity
- Web Development

## Disclaimer

SECUREFACE X is an academic and research-oriented prototype developed for controlled biometric-security experimentation and defensive security demonstration.

The Attack Lab is designed to test the security controls of the local application and its own protected resources.

The system should not be considered production-ready biometric infrastructure without additional controls for liveness detection, cryptographic key management, privacy, secure deployment, authentication policy, monitoring, compliance and operational security.
