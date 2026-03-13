import time
import psutil
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# ตัวแปรเก็บสถิติชั่วคราว (ในระดับ Production แนะนำให้ใช้ Redis)
state = {
    "request_count": 0,
    "last_reset": time.time()
}

@app.middleware("http")
async def count_requests(request: Request, call_next):
    state["request_count"] += 1
    response = await call_next(request)
    return response

@app.get("/api/stats")
async def get_stats():
    # คำนวณ Requests Per Second (RPS) โดยประมาณ
    now = time.time()
    elapsed = now - state["last_reset"]
    rps = state["request_count"] / elapsed if elapsed > 0 else 0
    
    # รีเซ็ตตัวนับทุกช่วงเวลาสั้นๆ เพื่อความแม่นยำของกราฟ
    if elapsed > 5: 
        state["request_count"] = 0
        state["last_reset"] = now

    net = psutil.net_io_counters()
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "rps": round(rps, 2),
        "net_sent": net.bytes_sent,
        "net_recv": net.bytes_recv,
        "disk": psutil.disk_usage('/').percent,
        "load_avg": psutil.getloadavg()[0] # Load 1 min
    }

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
