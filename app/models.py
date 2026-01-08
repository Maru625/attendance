from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    name: str

class CheckInRequest(BaseModel):
    name: str
    location: str
    employee_id: str
    time: Optional[str] = None # Optional manual time
    date: Optional[str] = None # Optional past date (YYYY-MM-DD)

class CheckOutRequest(BaseModel):
    name: str
    employee_id: str
    time: Optional[str] = None # Optional manual time
    date: Optional[str] = None # Optional past date (YYYY-MM-DD)

class UpdateRecordRequest(BaseModel):
    employee_id: str
    date: str
    field: str # 'checkin' or 'checkout'
    value: str

class DeleteRecordRequest(BaseModel):
    employee_id: str
    date: str
