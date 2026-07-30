from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import qrcode
import io
import base64
import os

app = Flask(__name__)
# อนุญาตให้ Frontend ยิง Request เข้ามาได้
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'local_data.db')

# ฟังก์ชันสร้างตารางฐานข้อมูล (ถ้ายังไม่มี)
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                description TEXT NOT NULL,
                link TEXT NOT NULL,
                qr_base64 TEXT NOT NULL
            )
        ''')
        conn.commit()

# Route 1: สำหรับดึงข้อมูลทั้งหมดไปแสดงตอนเปิดเว็บใหม่
@app.route('/api/data', methods=['GET'])
def get_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, description, link, qr_base64 FROM entries ORDER BY id DESC")
        rows = cursor.fetchall()
        
        # แปลงข้อมูลให้อยู่ในรูป Dictionary เพื่อส่งเป็น JSON
        data = [{"username": r[0], "description": r[1], "link": r[2], "qr_base64": r[3]} for r in rows]
    return jsonify(data)

# Route 2: สำหรับรับข้อมูลใหม่ สร้าง QR Code แล้วบันทึก
@app.route('/api/submit', methods=['POST'])
def submit_data():
    req_data = request.json
    username = req_data.get('username')
    description = req_data.get('description')
    link = req_data.get('link')

    if not all([username, description, link]):
        return jsonify({"error": "Missing data! กรอกให้ครบทุกช่อง"}), 400

    # 1. สร้าง QR Code จาก link ที่ส่งมา
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 2. แปลงรูป QR Code เป็นข้อความ (Base64) เพื่อจะได้ส่งไปหน้าเว็บง่ายๆ
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    qr_data_uri = f"data:image/png;base64,{qr_base64}"

    # 3. บันทึกลงฐานข้อมูล SQLite
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entries (username, description, link, qr_base64) VALUES (?, ?, ?, ?)",
            (username, description, link, qr_data_uri)
        )
        conn.commit()

    return jsonify({"message": "Saved successfully!", "qr_code": qr_data_uri}), 201

# Route 3: สำหรับปุ่ม Clear All Data
@app.route('/api/clear', methods=['DELETE'])
def clear_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries")
        conn.commit()
    return jsonify({"message": "All data cleared!"}), 200

if __name__ == '__main__':
    # รันฐานข้อมูลก่อนเป็นอันดับแรก
    init_db()
    # รันเซิร์ฟเวอร์ (0.0.0.0 เพื่อให้เครื่องอื่นในวง LAN เข้ามาเรียก API ได้ด้วย)
    app.run(host='0.0.0.0', port=8000, debug=True)