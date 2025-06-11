from fastapi import FastAPI
from pydantic import BaseModel
from geopy.distance import geodesic
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI()

# السماح بالطلبات من أي مصدر (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← يمكنك تقييدها لاحقًا
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# الموقع الصحيح
TARGET_LOCATION = (45.06777191162109, 38.94906616210938)
MAX_DISTANCE_KM = 0.1  # 100 متر

# نموذج البيانات
class AttendanceData(BaseModel):
    qr_data: str
    lat: float
    lon: float
    device_id: str  # ← معرف الجهاز


@app.post("/api/attendance")
async def record_attendance(data: AttendanceData):
    print("📥 Received data:", data)

    user_location = (data.lat, data.lon)
    distance = geodesic(user_location, TARGET_LOCATION).km
    print(f"📍 Distance to target: {distance:.4f} km")

    if distance > MAX_DISTANCE_KM:
        print("❌ Out of allowed area.")
        return {"status": "failed", "reason": "Out of allowed area"}

    # الحصول على الوقت الحالي
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # تحضير السطر للحفظ
    log_line = f"{timestamp} | QR: {data.qr_data} | Device: {data.device_id} | Location: ({data.lat}, {data.lon})\n"


    # تحديد المسار المطلق (اختياري لضمان الحفظ الصحيح)
    log_file = os.path.join(os.path.dirname(__file__), "attendance_log.txt")

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
        print("✅ Attendance saved.")
        return {"status": "success", "message": "Attendance recorded"}
    except Exception as e:
        print("❌ Error writing to file:", e)
        return {"status": "error", "message": "Could not save attendance"}
