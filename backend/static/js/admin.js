document.addEventListener('DOMContentLoaded', async () => {
    const tableBody = document.querySelector('#requestsTable tbody');
    const feedbackTableBody = document.querySelector('#feedbackTable tbody');

    // Chức năng tải và hiển thị bảng yêu cầu gần đây
  let currentPage = 1;
    const itemsPerPage = 5;
    let allLogs = []; // Lưu trữ tất cả logs

    const createPagination = (totalItems) => {
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        const paginationContainer = document.createElement('div');
        paginationContainer.className = 'pagination';
        paginationContainer.innerHTML = `
            <button onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Previous</button>
            <span>Page ${currentPage} of ${totalPages}</span>
            <button onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>
        `;
        return paginationContainer;
    };

    const displayLogs = (page) => {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const paginatedLogs = allLogs.slice(start, end);

        if (tableBody) {
            tableBody.innerHTML = '';
            
            paginatedLogs.forEach(log => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${log.ip_address}</td>
                    <td>${log.request_time}</td>
                    <td>${log.filename || 'N/A'}</td>
                    <td>${log.prediction || 'N/A'}</td>
                    <td>${(log.confidence * 100).toFixed(2)}%</td>
                `;
                tableBody.appendChild(row);
            });

            // Thêm phân trang sau bảng
            const existingPagination = document.querySelector('.pagination');
            if (existingPagination) {
                existingPagination.remove();
            }
            tableBody.parentElement.parentElement.insertAdjacentElement('afterend', createPagination(allLogs.length));
        }
    };

    // Thêm hàm changePage vào window object để có thể gọi từ onclick
    window.changePage = (page) => {
        if (page < 1 || page > Math.ceil(allLogs.length / itemsPerPage)) return;
        currentPage = page;
        displayLogs(currentPage);
    };

    // Cập nhật hàm fetchLogs
    const fetchLogs = async () => {
        try {
            const response = await fetch('/api/logs');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            allLogs = await response.json();
            displayLogs(currentPage);
        } catch (e) {
            console.error("Lỗi khi tải dữ liệu logs:", e);
            if (tableBody) {
                tableBody.innerHTML = '<tr><td colspan="6">Không thể tải dữ liệu log. Vui lòng kiểm tra backend.</td></tr>';
            }
        }
    };

    // Chức năng tải và hiển thị bảng phản hồi sai
    const fetchFeedbackLogs = async () => {
        try {
            const response = await fetch('/api/stats/feedback');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const logs = await response.json();

            if (feedbackTableBody) {
                feedbackTableBody.innerHTML = '';
            }
            
            logs.forEach(log => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${log.created_at}</td>
                    <td><img src="data:image/png;base64,${log.image_data}" alt="Feedback Image" style="width: 100px; height: auto;"></td>
                    <td>${log.label}</td>
                `;
                feedbackTableBody.appendChild(row);
            });
        } catch (e) {
            console.error("Lỗi khi tải dữ liệu phản hồi:", e);
            if (feedbackTableBody) {
                feedbackTableBody.innerHTML = '<tr><td colspan="3">Không thể tải dữ liệu phản hồi. Vui lòng kiểm tra backend.</td></tr>';
            }
        }
    };
    
    // Gọi tất cả các hàm để tải dữ liệu khi trang được tải
    fetchLogs();
    fetchFeedbackLogs();
});