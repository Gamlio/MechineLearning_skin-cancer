# backend/app.py

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template
from flask_cors import CORS
import torch
import torch.nn as nn
# Import the correct EfficientNet library
from efficientnet_pytorch import EfficientNet

# Import the blueprint from routes.py
from api.routes import api_blueprint

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Tải mô hình đã huấn luyện
try:
    # Use the same model architecture as the one used for training
    model = EfficientNet.from_name('efficientnet-b0')
    num_ftrs = model._fc.in_features
    model._fc = nn.Linear(num_ftrs, 3)
    
    # Load the trained model weights
    model.load_state_dict(torch.load('EfficientNet-B0_trained.pth', map_location=torch.device('cpu')))
    
    model.eval()
    app.config['MODEL'] = model
    print("Mô hình EfficientNet-B0 đã được tải thành công!")
except FileNotFoundError:
    print("Không tìm thấy file 'EfficientNet-B0_trained.pth'. Vui lòng kiểm tra lại đường dẫn.")
    app.config['MODEL'] = None
except Exception as e:
    print(f"Lỗi khi tải mô hình: {e}")
    app.config['MODEL'] = None

app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/')
def redirect_to_admin():
    return render_template('admin.html')
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)
