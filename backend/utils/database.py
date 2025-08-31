import psycopg2
import os
from dotenv import load_dotenv
import base64

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

def get_db_connection():
    """Tạo và trả về một kết nối đến cơ sở dữ liệu."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print("Kết nối database thành công.")
        return conn
    except Exception as e:
        print(f"Lỗi khi kết nối database: {e}")
        print("Vui lòng kiểm tra file .env và đảm bảo dịch vụ PostgreSQL đang chạy.")
        return None

def insert_request_log(ip_address, filename, prediction, confidence, is_valid):
    """Ghi lại thông tin request vào bảng requests và trả về id của bản ghi."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        cur = conn.cursor()
        
        sql = """
            INSERT INTO requests (ip_address, request_time, filename, prediction, confidence, is_valid_case)
            VALUES (%s, NOW(), %s, %s, %s, %s) RETURNING id;
        """
        
        is_valid_str = 'TRUE' if is_valid else 'FALSE'
        
        cur.execute(sql, (ip_address, filename, prediction, confidence, is_valid_str))
        log_id = cur.fetchone()[0]
        conn.commit()
        print("Log request đã được ghi vào database thành công.")
        return log_id
    except Exception as e:
        print(f"Lỗi khi ghi log request: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            cur.close()
            conn.close()

def update_request_log_invalidity_by_id(log_id):
    """Cập nhật is_valid_case của một bản ghi trong bảng requests thành FALSE dựa trên ID."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cur = conn.cursor()
        sql = """
            UPDATE requests SET is_valid_case = FALSE WHERE id = %s;
        """
        cur.execute(sql, (log_id,))
        conn.commit()
        print(f"Đã cập nhật trạng thái không hợp lệ cho log ID: {log_id}")
    except Exception as e:
        print(f"Lỗi khi cập nhật log: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def get_request_logs():
    """Lấy toàn bộ dữ liệu log request từ database."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cur = conn.cursor()
        cur.execute("SELECT * FROM requests ORDER BY request_time DESC;")
        columns = [desc[0] for desc in cur.description]
        logs = [dict(zip(columns, row)) for row in cur.fetchall()]
        return logs
    except Exception as e:
        print(f"Lỗi khi lấy logs: {e}")
        return []
    finally:
        if conn:
            cur.close()
            conn.close()

def insert_feedback_log(image_data, label):
    """Lưu dữ liệu phản hồi vào database."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            return
        cur = conn.cursor()
        
        # Bóc chuỗi tiền tố 'data:image/png;base64,'
        if 'base64,' in image_data:
            base64_data = image_data.split('base64,')[1]
        else:
            base64_data = image_data
            
        # Giải mã chuỗi base64 thành dữ liệu nhị phân
        decoded_image_data = base64.b64decode(base64_data)
        
        sql = """
            INSERT INTO feedback (image_data, label, created_at)
            VALUES (%s, %s, NOW());
        """
        
        cur.execute(sql, (decoded_image_data, label))
        conn.commit()
        print("Log phản hồi đã được ghi vào database thành công.")
    except Exception as e:
        print(f"Lỗi khi ghi log phản hồi: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def get_prediction_counts():
    """Lấy số lượng dự đoán cho mỗi nhãn từ bảng requests, bao gồm cả các nhãn có số lượng 0."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            return {}
        cur = conn.cursor()
        
        counts = {'BCC': 0, 'SCC': 0, 'Mel': 0}
        
        cur.execute("SELECT prediction, COUNT(*) FROM requests WHERE is_valid_case = TRUE GROUP BY prediction;")
        db_counts = dict(cur.fetchall())
        
        for key, value in db_counts.items():
            if key in counts:
                counts[key] = value
                
        return counts
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu thống kê dự đoán: {e}")
        return {}
    finally:
        if conn:
            cur.close()
            conn.close()

def get_feedback_logs():
    """Lấy toàn bộ dữ liệu phản hồi từ bảng feedback."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cur = conn.cursor()
        cur.execute("SELECT created_at, label, encode(image_data, 'base64') as image_data FROM feedback ORDER BY created_at DESC;")
        columns = [desc[0] for desc in cur.description]
        logs = [dict(zip(columns, row)) for row in cur.fetchall()]
        return logs
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu phản hồi: {e}")
        return []
    finally:
        if conn:
            cur.close()
            conn.close()
