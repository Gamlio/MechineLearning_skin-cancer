import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models
import io

def predict_image(file, model):
    if model is None:
        raise Exception('Mô hình chưa được tải. Không thể dự đoán.')

    classes = ['BCC', 'SCC', 'Mel']
    image = Image.open(io.BytesIO(file.read())).convert('RGB')
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    predicted_class = classes[predicted.item()]
    confidence_score = confidence.item()

    return predicted_class, confidence_score