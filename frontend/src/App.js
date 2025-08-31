import React, { useState } from 'react';
import './App.css'; // Import the CSS file

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [logId, setLogId] = useState(null); // State mới để lưu log_id
  const [message, setMessage] = useState(''); // State mới để hiển thị thông báo

  const handleFileChange = (file) => {
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setPrediction(null);
      setError(null);
      setShowFeedback(false);
      setLogId(null);
      setMessage('');
    }
  };

  const handlePredict = async () => {
    if (!selectedFile) {
      setError("Vui lòng chọn một file ảnh.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setShowFeedback(false);
    setMessage('');

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data);
      setLogId(data.log_id); // Lưu log_id từ phản hồi của máy chủ
      setShowFeedback(true);

    } catch (e) {
      console.error("Lỗi khi dự đoán:", e);
      setError("Đã xảy ra lỗi khi dự đoán. Vui lòng thử lại.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendFeedback = async (correctLabel) => {
    if (!selectedFile || !logId) { // Kiểm tra cả logId
      setError("Không có ảnh hoặc log ID để gửi phản hồi.");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("label", correctLabel);
    formData.append("log_id", logId); // Gửi log_id đi

    try {
      const response = await fetch('http://localhost:5000/api/feedback', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      setMessage(`Cảm ơn bạn! Phản hồi "${correctLabel}" đã được gửi thành công.`);
      setShowFeedback(false);
      
      // Tự động ẩn thông báo sau 3 giây
      setTimeout(() => {
        setMessage('');
      }, 3000);

    } catch (e) {
      console.error("Lỗi khi gửi phản hồi:", e);
      setError("Đã xảy ra lỗi khi gửi phản hồi. Vui lòng thử lại.");
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleFileChange(file);
    } else {
      setError("File được kéo thả phải là một file ảnh.");
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Ứng Dụng Phân Loại Ung Thư Da</h1>
      </header>
      <main className="App-main">
        <div className="main-content">
          {/* Left Side: Input and Predict Button */}
          <div className="input-predict-container">
            <div
              className="drop-area"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <p>Kéo và thả ảnh vào đây, hoặc</p>
              <input
                type="file"
                id="image-upload"
                accept="image/*"
                onChange={(e) => handleFileChange(e.target.files[0])}
                hidden
              />
              <label htmlFor="image-upload" className="upload-btn">
                Chọn ảnh
              </label>
            </div>
            <button onClick={handlePredict} className="predict-btn" disabled={isLoading || !selectedFile}>
              {isLoading ? "Đang xử lý..." : "Dự đoán Ngay"}
            </button>
          </div>
          
          {/* Right Side: Image and Results Display */}
          {(previewUrl || prediction || error) && (
              <div className="display-area-container">
                  {previewUrl && (
                      <div className="image-preview-container">
                          <img src={previewUrl} alt="Preview" className="image-preview" />
                      </div>
                  )}
                  {prediction && (
                      <div className="result-container">
                          <h2>Kết quả Dự đoán</h2>
                          <p className="prediction-text">
                              Kết quả: <span className={`prediction-label ${prediction.prediction.toLowerCase()}`}>{prediction.prediction}</span>
                          </p>
                          <p className="confidence-text">
                              Độ tin cậy: <span className="confidence-score">{(prediction.confidence * 100).toFixed(2)}%</span>
                          </p>
                      </div>
                  )}
                  {error && (
                      <div className="result-container error">
                          <p>{error}</p>
                      </div>
                  )}
              </div>
          )}
        </div>

        {/* Bottom Center: Feedback */}
        {showFeedback && prediction && (
            <div className="feedback-container">
                <h3>Dự đoán sai?</h3>
                <p>Kết quả dự đoán có thể chưa chính xác. Vui lòng chọn nhãn đúng để giúp chúng tôi cải thiện mô hình:</p>
                <div className="feedback-buttons">
                    <button onClick={() => handleSendFeedback('BCC')} className="feedback-btn bcc">BCC</button>
                    <button onClick={() => handleSendFeedback('SCC')} className="feedback-btn scc">SCC</button>
                    <button onClick={() => handleSendFeedback('MEL')} className="feedback-btn mel">MEL</button>
                </div>
            </div>
        )}
      </main>
      
      {/* Success/Error Message Display */}
      {message && (
        <div className="message-box success">
          <p>{message}</p>
        </div>
      )}

      <footer className="App-footer">
          <p>© 2024 Ứng Dụng Phân Loại Ung Thư Da.được làm bới nhóm 9 CNTT K21B.</p>
      </footer>
    </div>
  );
}

export default App;
