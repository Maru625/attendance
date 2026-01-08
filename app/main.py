from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.models import LoginRequest, CheckInRequest, CheckOutRequest, UpdateRecordRequest, DeleteRecordRequest
import app.services.sheet_service as sheet_service
import uvicorn
import os
import asyncio
import queue

app = FastAPI()

# Log Manager
class LogManager:
    def __init__(self):
        self.listeners = []

    def log(self, message: str):
        print(message) # Keep terminal output
        for q in self.listeners:
            q.put_nowait(message)

    async def stream_log(self):
        q = queue.Queue()
        self.listeners.append(q)
        try:
            while True:
                # Check for new messages
                try:
                    msg = q.get_nowait()
                    yield f"data: {msg}\n\n"
                    # Small delay to batch sending or yield back control
                except queue.Empty:
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            self.listeners.remove(q)

log_manager = LogManager()
sheet_service.set_log_callback(log_manager.log)

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (HTML, CSS, JS)
# Ensure the 'app/static' directory exists before running
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# Routes
@app.get("/")
async def root():
    return {"message": "Kada Commute API Running"}

@app.get("/api/stream-logs")
async def stream_logs():
    return StreamingResponse(log_manager.stream_log(), media_type="text/event-stream")

@app.post("/api/login")
async def login(request: LoginRequest):
    spreadsheet = sheet_service.connect_to_spreadsheet()
    if not spreadsheet:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    employee = sheet_service.find_employee(spreadsheet, request.name)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee

@app.post("/api/check-in")
async def check_in(request: CheckInRequest):
    spreadsheet = sheet_service.connect_to_spreadsheet()
    if not spreadsheet:
         raise HTTPException(status_code=500, detail="Database connection failed")
    
    # Construct employee dict as expected by sheet_service
    employee = {
        'name': request.name,
        'location': request.location,
        'id': request.employee_id
    }
    
    success = sheet_service.check_in(spreadsheet, employee, specific_time=request.time, specific_date=request.date)
    if not success:
        raise HTTPException(status_code=400, detail="Check-in failed")
    
    return {"status": "success", "message": "Check-in successful"}

@app.post("/api/check-out")
async def check_out(request: CheckOutRequest):
    spreadsheet = sheet_service.connect_to_spreadsheet()
    if not spreadsheet:
         raise HTTPException(status_code=500, detail="Database connection failed")

    employee = {
        'name': request.name,
        'id': request.employee_id
    }

    success = sheet_service.check_out(spreadsheet, employee, specific_time=request.time, specific_date=request.date)
    if not success:
        raise HTTPException(status_code=400, detail="Check-out failed (maybe no record for today?)")
    
    return {"status": "success", "message": "Check-out successful"}

@app.get("/api/history/{employee_id}")
async def get_history(employee_id: str):
    spreadsheet = sheet_service.connect_to_spreadsheet()
    if not spreadsheet:
         raise HTTPException(status_code=500, detail="Database connection failed")
    
    records = sheet_service.get_all_employee_records(spreadsheet, employee_id)
    return records

@app.put("/api/record")
async def update_record(request: UpdateRecordRequest):
    spreadsheet = sheet_service.connect_to_spreadsheet()
    if not spreadsheet:
         raise HTTPException(status_code=500, detail="Database connection failed")
    
    checkin_val = request.value if request.field == 'checkin' else None
    checkout_val = request.value if request.field == 'checkout' else None

    success = sheet_service.update_record(spreadsheet, request.employee_id, request.date, checkin=checkin_val, checkout=checkout_val)
    if not success:
         raise HTTPException(status_code=400, detail="Update failed")
    
    return {"status": "success", "message": "Record updated"}

@app.delete("/api/record")
async def delete_record(request: DeleteRecordRequest):
    spreadsheet = sheet_service.connect_to_spreadsheet()
    if not spreadsheet:
         raise HTTPException(status_code=500, detail="Database connection failed")
    
    success = sheet_service.delete_record(spreadsheet, request.employee_id, request.date)
    if not success:
         raise HTTPException(status_code=400, detail="Delete failed")
    
    return {"status": "success", "message": "Record deleted"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
