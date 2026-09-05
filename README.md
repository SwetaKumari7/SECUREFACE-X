# SECUREFACE X

### Security-Enhanced Deep Learning Based Face Biometric Authentication System

<p align="center">
  <b>Deep Learning • Biometric Authentication • Template Security • Threat Detection • SOC Monitoring</b>
</p>

---

## Overview

**SECUREFACE X** is a security-focused face biometric authentication system designed to demonstrate how deep-learning-based facial recognition can be strengthened with practical cybersecurity controls.

The system uses a **pretrained FaceNet/InceptionResNetV1 model** to generate 512-dimensional facial embeddings and performs identity verification using cosine similarity. Registered biometric templates are protected using **AES-256-CBC encryption**, while **SHA-256 integrity verification** and a **local hash-chained tamper-evident ledger** provide additional protection against unauthorized modification.

The system also incorporates authentication-abuse detection, temporary account lockout, security-event logging, and a **Security Operations Center (SOC)-style dashboard** for monitoring biometric security events.

---

## Key Highlights

- Face detection using **MTCNN**
- Face representation using **FaceNet / InceptionResNetV1**
- 512-dimensional facial embeddings
- Pretrained **VGGFace2** weights
- Cosine similarity-based identity verification
- AES-256-CBC encrypted biometric templates
- SHA-256 template integrity verification
- Hash-chained tamper-evident ledger
- Authentication abuse detection
- Three-attempt temporary lockout
- Security-event logging
- SQLite-based audit storage
- SOC-style security monitoring dashboard
- Controlled defensive biometric Attack Lab
- ROC, AUC, FAR, FRR and F1-based evaluation

---

## System Architecture

```text
                         INPUT FACE IMAGE
                                |
                                v
                       +----------------+
                       |  MTCNN Face    |
                       |   Detection    |
                       +-------+--------+
                               |
                               v
                    +-----------------------+
                    | FaceNet /             |
                    | InceptionResNetV1     |
                    +----------+------------+
                               |
                               v
                       512-D EMBEDDING
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
        REGISTERED TEMPLATE           INPUT EMBEDDING
                 |                           |
                 v                           |
          AES-256-CBC                       |
          Protected Storage                 |
                 |                           |
                 v                           |
          SHA-256 Integrity                 |
                 |                           |
                 v                           |
        Hash-Chained Ledger                 |
                 |                           |
                 +-------------+-------------+
                               |
                               v
                     Cosine Similarity
                               |
                     +---------+---------+
                     |                   |
                     v                   v
                  MATCH               NO MATCH
                     |                   |
                     v                   v
                VERIFIED              REJECTED
                                         |
                                         v
                              Failed Attempt Monitor
                                         |
                                  3 Failed Attempts
                                         |
                                         v
                                  TEMPORARY LOCKOUT
                                         |
                                         v
                                  SECURITY EVENT
                                         |
                                         v
                                  SOC DASHBOARD
