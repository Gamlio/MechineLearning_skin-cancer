import numpy as np

# Định nghĩa các lớp phân loại ung thư da
classes = ['BCC', 'SCC', 'Mel']

def get_loss_chart_data():
    # Dữ liệu giả định
    epochs = list(range(1, 11))
    training_loss = [0.6, 0.4, 0.3, 0.2, 0.15, 0.12, 0.1, 0.08, 0.07, 0.06]
    validation_loss = [0.7, 0.5, 0.4, 0.3, 0.25, 0.2, 0.18, 0.17, 0.16, 0.15]
    
    return {
        'title': 'Biểu đồ Loss',
        'labels': epochs,
        'datasets': [
            {'label': 'Training Loss', 'data': training_loss, 'borderColor': 'blue'},
            {'label': 'Validation Loss', 'data': validation_loss, 'borderColor': 'red'}
        ]
    }

def get_confusion_matrix_data():
    # Dữ liệu giả định
    num_classes = len(classes)
    matrix = np.random.randint(0, 20, size=(num_classes, num_classes)).tolist()
    # Làm cho đường chéo chính lớn hơn để mô phỏng kết quả tốt
    for i in range(num_classes):
        matrix[i][i] = matrix[i][i] + 50
    
    return {
        'title': 'Ma trận nhầm lẫn (Confusion Matrix)',
        'labels': classes,
        'matrix': matrix
    }