import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1


# --------------------------------------------------
# Device
# --------------------------------------------------

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# --------------------------------------------------
# Face detector
# --------------------------------------------------

mtcnn = MTCNN(
    image_size=160,
    margin=20,
    min_face_size=20,
    keep_all=False,
    post_process=True,
    device=DEVICE
)


# --------------------------------------------------
# FaceNet model
# --------------------------------------------------

facenet = InceptionResnetV1(
    pretrained="vggface2"
).eval().to(DEVICE)


# --------------------------------------------------
# Generate face embedding
# --------------------------------------------------

def get_embedding(image_path):
    """
    Detects a face in an image and generates
    a normalized 512-dimensional FaceNet embedding.
    """

    image = Image.open(image_path).convert("RGB")

    face = mtcnn(image)

    if face is None:
        raise ValueError("No face detected in the image.")

    face = face.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        embedding = facenet(face)

    embedding = embedding.cpu().numpy()[0]

    # Normalize embedding
    norm = np.linalg.norm(embedding)

    if norm == 0:
        raise ValueError("Invalid face embedding.")

    embedding = embedding / norm

    return embedding


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    print("Face Engine Loaded")
    print("Device:", DEVICE)
    print("Embedding size: 512")