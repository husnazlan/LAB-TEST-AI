import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import requests
import pandas as pd

st.set_page_config(
    page_title="Real-Time Image Classification",
    layout="centered"
)

st.title("Real-Time Webcam Image Classification")
st.write("Using **ResNet-18 pretrained on ImageNet**")

@st.cache_data
def load_labels():
    url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
    labels = requests.get(url).text.splitlines()
    return labels

@st.cache_resource
def load_model():
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()
    return model

labels = load_labels()
model = load_model()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

st.subheader("Capture Image from Webcam")
img_data = st.camera_input("Take a photo")

if img_data is not None:
    image = Image.open(img_data).convert("RGB")
    st.image(image, caption="Captured Image", use_container_width=True)

    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)

    with torch.no_grad():
        outputs = model(input_batch)
        probs = F.softmax(outputs[0], dim=0)

    top5_prob, top5_catid = torch.topk(probs, 5)

    st.subheader("Top 5 Predictions")
    for i in range(5):
        st.write(f"{labels[top5_catid[i]]} : {top5_prob[i].item():.4f}")

    df = pd.DataFrame({
        "Label": [labels[idx] for idx in top5_catid],
        "Probability": [float(p) for p in top5_prob]
    })

    st.subheader("Prediction Table")
    st.dataframe(df)

else:
    st.info("Click **Take a photo** to start classification.")
