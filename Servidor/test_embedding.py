"""
Test embedding generation
"""
import cv2
import numpy as np
from deepface import DeepFace

# Create a simple test image (black square with white circle = fake face)
img = np.zeros((200, 200, 3), dtype=np.uint8)
cv2.circle(img, (100, 100), 50, (255, 255, 255), -1)

print("Testing embedding generation...")
print(f"Image shape: {img.shape}")

# Test with Facenet512
try:
    result = DeepFace.represent(
        img_path=img,
        model_name="Facenet512",
        detector_backend="opencv",
        enforce_detection=False
    )
    
    if result:
        embedding = result[0]["embedding"]
        print(f"\nFacenet512 embedding dimension: {len(embedding)}")
        print(f"Embedding type: {type(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    else:
        print("No face detected")
        
except Exception as e:
    print(f"Error: {str(e)}")
