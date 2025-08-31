import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
import torch
from PIL import Image
from io import BytesIO
import base64

# Nhập các hàm từ các file khác
from core.model import predict_image
from utils.database import insert_request_log, get_request_logs, insert_feedback_log, get_prediction_counts, get_feedback_logs, update_request_log_invalidity_by_id

api_blueprint = Blueprint('api', __name__)

# Khởi tạo thư mục lưu trữ phản hồi
FEEDBACK_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'feedback_data')
for label in ['BCC', 'SCC', 'Mel']:
    os.makedirs(os.path.join(FEEDBACK_FOLDER, label), exist_ok=True)

# Định nghĩa các lớp
class_names = ['BCC', 'SCC', 'Mel']

@api_blueprint.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        print("Error: No image file provided")
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        print("Error: No selected file")
        return jsonify({'error': 'No selected file'}), 400

    try:
        model = current_app.config.get('MODEL')
        if model is None:
            print("Error: Model not loaded")
            return jsonify({"error": "Mô hình chưa được tải"}), 500
        
        file.seek(0)
        image_bytes = file.read()
        image_stream = BytesIO(image_bytes)
        
        prediction, confidence = predict_image(image_stream, model)
        
        # Ghi log và nhận ID duy nhất của bản ghi
        log_id = insert_request_log(request.remote_addr, file.filename, prediction, confidence, True)

        print(f"Prediction successful: {prediction} with confidence {confidence}, Log ID: {log_id}")
        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'log_id': log_id
        })
    except Exception as e:
        print(f"Prediction failed with error: {e}")
        insert_request_log(request.remote_addr, file.filename, "Error", 0, False)
        return jsonify({'error': f'Lỗi khi dự đoán: {str(e)}'}), 500

@api_blueprint.route('/feedback', methods=['POST'])
def feedback():
    """
    Nhận ảnh, nhãn đúng và ID log từ người dùng để lưu trữ và cập nhật trạng thái.
    """
    if 'image' not in request.files or 'label' not in request.form or 'log_id' not in request.form:
        print("Error: Missing image file, label, or log_id in feedback request")
        return jsonify({"error": "Thiếu file ảnh, nhãn hoặc log_id"}), 400

    file = request.files['image']
    label = request.form['label']
    log_id = request.form['log_id']
    
    if label not in ['BCC', 'SCC', 'Mel']:
        print(f"Error: Invalid label '{label}' provided")
        return jsonify({"error": "Nhãn không hợp lệ"}), 400

    if file:
        try:
            image_data = file.read()
            image_data_base64 = base64.b64encode(image_data).decode('utf-8')
            
            insert_feedback_log(image_data_base64, label)
            
            update_request_log_invalidity_by_id(log_id)
            
            print(f"Feedback successfully saved for label: {label} for log ID: {log_id}")
            return jsonify({"message": "Phản hồi đã được lưu thành công"}), 200
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return jsonify({"error": f"Lỗi khi lưu phản hồi: {e}"}), 500

    print("Error: Unknown error while processing feedback")
    return jsonify({"error": "Lỗi không xác định khi xử lý phản hồi"}), 500

# Endpoint để lấy dữ liệu log cho trang admin
@api_blueprint.route('/logs', methods=['GET'])
def get_logs():
    try:
        logs = get_request_logs()
        return jsonify(logs)
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return jsonify({'error': 'Lỗi khi lấy dữ liệu logs'}), 500

# Endpoint mới để lấy dữ liệu thống kê dự đoán
@api_blueprint.route('/stats/predictions', methods=['GET'])
def get_prediction_stats():
    try:
        counts = get_prediction_counts()
        return jsonify(counts)
    except Exception as e:
        print(f"Error fetching prediction stats: {e}")
        return jsonify({'error': 'Lỗi khi lấy dữ liệu thống kê dự đoán'}), 500

# Endpoint mới để lấy dữ liệu phản hồi sai (phản hồi người dùng)
@api_blueprint.route('/stats/feedback', methods=['GET'])
def get_feedback_stats():
    try:
        feedback_logs = get_feedback_logs()
        return jsonify(feedback_logs)
    except Exception as e:
        print(f"Error fetching feedback stats: {e}")
        return jsonify({'error': 'Lỗi khi lấy dữ liệu phản hồi'}), 500