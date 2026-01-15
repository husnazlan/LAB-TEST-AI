import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import requests

# -----------------------
# Step 1: Import Libraries
# -----------------------

st.title("Real-Time Image Classification (ResNet-18)")
st.write("Upload or capture an image and classify using a pretrained ResNet-18 model.")

# -----------------------
# Step 2: Load ImageNet Labels
# -----------------------

LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
response = requests.get(LABELS_URL)
imagenet_classes = response.text.splitlines()

# -----------------------
# Step 3: Load Pretrained Model
# -----------------------

model = models.resnet18(pretrained=True)
model.eval()  # set to eval mode

# -----------------------
# Step 4: Define Preprocessing
# -----------------------

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

# -----------------------
# Step 5: Capture or Upload Image
# -----------------------

img_file = st.camera_input("Capture an Image")  # webcam input

if img_file is None:
    img_file = st.file_uploader("Or upload an image", type=["jpg", "jpeg", "png"])

if img_file is not None:
    image = Image.open(img_file)
    st.image(image, caption="Input Image", use_column_width=True)

    # Preprocess
    img_tensor = preprocess(image)
    batch_tensor = img_tensor.unsqueeze(0)  # add batch size

    # -----------------------
    # Step 6: Run Prediction
    # -----------------------
    with torch.no_grad():
        outputs = model(batch_tensor)
        probabilities = F.softmax(outputs[0], dim=0)

    # Top-5 Predictions
    top5_prob, top5_idx = torch.topk(probabilities, 5)

    st.subheader("Top-5 Predictions")
    results = []

    for i in range(5):
        label = imagenet_classes[top5_idx[i]]
        prob = float(top5_prob[i].item()) * 100
        results.append((label, f"{prob:.2f}%"))

    st.table(results)
