// ชี้ไปที่พอร์ต 8000
const API_BASE = 'http://localhost:8000/api';

// โหลดข้อมูลทันทีที่เปิดเว็บ
document.addEventListener('DOMContentLoaded', loadData);

// จัดการเมื่อกดปุ่ม Submit
document.getElementById('dataForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // ป้องกันเว็บรีเฟรช

    const submitBtn = document.querySelector('.btn-submit');
    submitBtn.textContent = 'Generating...';
    submitBtn.disabled = true;

    const payload = {
        username: document.getElementById('username').value,
        description: document.getElementById('description').value,
        link: document.getElementById('link').value
    };

    try {
        const response = await fetch(`${API_BASE}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById('dataForm').reset();
            loadData(); // ดึงข้อมูลใหม่มาแสดง
        } else {
            alert('Oops! Something went wrong.');
        }
    } catch (error) {
        alert('Cannot connect to backend! อย่าลืมรัน python app.py');
        console.error(error);
    } finally {
        submitBtn.textContent = 'Generate QR Code';
        submitBtn.disabled = false;
    }
});

// ผูก Event Listener ให้ปุ่ม Clear All Data
document.getElementById('btnClear').addEventListener('click', clearData);

// ฟังก์ชันดึงข้อมูลมาแสดง
async function loadData() {
    const summaryPane = document.getElementById('summaryPane');
    
    try {
        const response = await fetch(`${API_BASE}/data`);
        const data = await response.json();

        if (data.length === 0) {
            summaryPane.innerHTML = '<div class="no-data">No information yet</div>';
            return;
        }

        // สร้าง HTML สำหรับข้อมูลแต่ละอัน
        summaryPane.innerHTML = data.map(item => `
            <div class="data-card">
                <div class="data-info">
                    <h3>${item.username}</h3>
                    <p>${item.description}</p>
                    <a href="${item.link}" target="_blank">${item.link}</a>
                </div>
                <div class="data-qr">
                    <img src="${item.qr_base64}" alt="QR Code">
                </div>
            </div>
        `).join('');

    } catch (error) {
        summaryPane.innerHTML = '<div class="no-data" style="color: #FF3B30;">Cannot connect to Python backend (Port 8000)</div>';
    }
}

// ฟังก์ชันล้างข้อมูลทั้งหมด
async function clearData() {
    if (!confirm('Are you sure you want to clear ALL data?!')) return;

    try {
        await fetch(`${API_BASE}/clear`, { method: 'DELETE' });
        loadData(); // รีเฟรชหน้าจอให้ว่างเปล่า
    } catch (error) {
        alert('Error clearing data!');
    }
}