from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from twilio.rest import Client
import pandas as pd
import io
import asyncio
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Twilio Configuration
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
twilio_client = None

if twilio_account_sid and twilio_auth_token:
    twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Enums
class NotificationType(str, Enum):
    SMS = "sms"
    VOICE = "voice"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"

# Models
class AdminUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    role: str = "admin"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: AdminUser

class Student(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    roll_number: str
    name: str
    email: Optional[str] = None
    department: str
    year: int
    parent_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudentCreate(BaseModel):
    roll_number: str
    name: str
    email: Optional[str] = None
    department: str
    year: int
    parent_id: str

class Parent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone_number: str
    email: Optional[str] = None
    relationship: str = "parent"
    preferred_language: str = "english"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ParentCreate(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    relationship: str = "parent"
    preferred_language: str = "english"

class Attendance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    date: str
    status: str  # present, absent
    subject: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AttendanceCreate(BaseModel):
    student_id: str
    date: str
    status: str
    subject: Optional[str] = None

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    parent_id: str
    type: NotificationType
    status: NotificationStatus
    message: str
    phone_number: str
    retry_count: int = 0
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VoiceTemplate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    language: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VoiceTemplateCreate(BaseModel):
    language: str
    message: str

class DashboardStats(BaseModel):
    total_students: int
    total_parents: int
    today_absentees: int
    notifications_sent_today: int
    failed_notifications: int

# Utility Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = await db.admin_users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return AdminUser(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def send_sms(phone_number: str, message: str) -> tuple[bool, Optional[str]]:
    """Send SMS via Twilio"""
    if not twilio_client:
        return False, "Twilio not configured"
    
    try:
        message_obj = twilio_client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone_number
        )
        return True, message_obj.sid
    except Exception as e:
        return False, str(e)

async def make_voice_call(phone_number: str, message: str) -> tuple[bool, Optional[str]]:
    """Make voice call via Twilio"""
    if not twilio_client:
        return False, "Twilio not configured"
    
    try:
        # Using Twilio's TwiML for voice
        twiml = f'<Response><Say language="en-IN">{message}</Say></Response>'
        call = twilio_client.calls.create(
            twiml=twiml,
            to=phone_number,
            from_=twilio_phone_number
        )
        return True, call.sid
    except Exception as e:
        return False, str(e)

async def process_attendance_and_notify(attendance_date: str):
    """Background task to process attendance and send notifications"""
    # Get all absent students for the date
    absent_records = await db.attendance.find(
        {"date": attendance_date, "status": "absent"},
        {"_id": 0}
    ).to_list(None)
    
    for record in absent_records:
        # Get student details
        student = await db.students.find_one({"id": record["student_id"]}, {"_id": 0})
        if not student:
            continue
        
        # Get parent details
        parent = await db.parents.find_one({"id": student["parent_id"]}, {"_id": 0})
        if not parent:
            continue
        
        # Get voice template for parent's language
        template = await db.voice_templates.find_one(
            {"language": parent.get("preferred_language", "english")},
            {"_id": 0}
        )
        
        message = f"Dear {parent['name']}, your child {student['name']} was absent on {attendance_date}. Please contact the college for details."
        if template:
            message = template["message"].replace("{parent_name}", parent['name']).replace("{student_name}", student['name']).replace("{date}", attendance_date)
        
        # Send SMS
        sms_success, sms_result = await send_sms(parent["phone_number"], message)
        
        sms_notification = {
            "id": str(uuid.uuid4()),
            "student_id": student["id"],
            "parent_id": parent["id"],
            "type": "sms",
            "status": "sent" if sms_success else "failed",
            "message": message,
            "phone_number": parent["phone_number"],
            "retry_count": 0,
            "error_message": None if sms_success else sms_result,
            "sent_at": datetime.now(timezone.utc).isoformat() if sms_success else None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(sms_notification)
        
        # Small delay before voice call
        await asyncio.sleep(2)
        
        # Make voice call
        voice_success, voice_result = await make_voice_call(parent["phone_number"], message)
        
        voice_notification = {
            "id": str(uuid.uuid4()),
            "student_id": student["id"],
            "parent_id": parent["id"],
            "type": "voice",
            "status": "sent" if voice_success else "failed",
            "message": message,
            "phone_number": parent["phone_number"],
            "retry_count": 0,
            "error_message": None if voice_success else voice_result,
            "sent_at": datetime.now(timezone.utc).isoformat() if voice_success else None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(voice_notification)

# Authentication Routes
@api_router.post("/auth/register", response_model=AdminUser)
async def register_admin(user: AdminUserCreate):
    existing = await db.admin_users.find_one({"email": user.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    admin_user = AdminUser(
        email=user.email,
        full_name=user.full_name
    )
    
    doc = admin_user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['hashed_password'] = hashed_password
    
    await db.admin_users.insert_one(doc)
    return admin_user

@api_router.post("/auth/login", response_model=Token)
async def login_admin(credentials: AdminLogin):
    user_doc = await db.admin_users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user_doc['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user_doc['id']})
    user = AdminUser(**{k: v for k, v in user_doc.items() if k != 'hashed_password'})
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.get("/auth/me", response_model=AdminUser)
async def get_me(current_user: AdminUser = Depends(get_current_user)):
    return current_user

# Student Routes
@api_router.post("/students", response_model=Student)
async def create_student(student: StudentCreate, current_user: AdminUser = Depends(get_current_user)):
    existing = await db.students.find_one({"roll_number": student.roll_number}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Roll number already exists")
    
    student_obj = Student(**student.model_dump())
    doc = student_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.students.insert_one(doc)
    return student_obj

@api_router.get("/students", response_model=List[Student])
async def get_students(current_user: AdminUser = Depends(get_current_user)):
    students = await db.students.find({}, {"_id": 0}).to_list(None)
    return students

@api_router.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str, current_user: AdminUser = Depends(get_current_user)):
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return Student(**student)

@api_router.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, student: StudentCreate, current_user: AdminUser = Depends(get_current_user)):
    existing = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student.model_dump()
    await db.students.update_one({"id": student_id}, {"$set": update_data})
    
    updated = await db.students.find_one({"id": student_id}, {"_id": 0})
    return Student(**updated)

@api_router.delete("/students/{student_id}")
async def delete_student(student_id: str, current_user: AdminUser = Depends(get_current_user)):
    result = await db.students.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

# Parent Routes
@api_router.post("/parents", response_model=Parent)
async def create_parent(parent: ParentCreate, current_user: AdminUser = Depends(get_current_user)):
    parent_obj = Parent(**parent.model_dump())
    doc = parent_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.parents.insert_one(doc)
    return parent_obj

@api_router.get("/parents", response_model=List[Parent])
async def get_parents(current_user: AdminUser = Depends(get_current_user)):
    parents = await db.parents.find({}, {"_id": 0}).to_list(None)
    return parents

@api_router.get("/parents/{parent_id}", response_model=Parent)
async def get_parent(parent_id: str, current_user: AdminUser = Depends(get_current_user)):
    parent = await db.parents.find_one({"id": parent_id}, {"_id": 0})
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    return Parent(**parent)

@api_router.put("/parents/{parent_id}", response_model=Parent)
async def update_parent(parent_id: str, parent: ParentCreate, current_user: AdminUser = Depends(get_current_user)):
    existing = await db.parents.find_one({"id": parent_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    update_data = parent.model_dump()
    await db.parents.update_one({"id": parent_id}, {"$set": update_data})
    
    updated = await db.parents.find_one({"id": parent_id}, {"_id": 0})
    return Parent(**updated)

@api_router.delete("/parents/{parent_id}")
async def delete_parent(parent_id: str, current_user: AdminUser = Depends(get_current_user)):
    result = await db.parents.delete_one({"id": parent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Parent not found")
    return {"message": "Parent deleted successfully"}

# Attendance Routes
@api_router.post("/attendance", response_model=Attendance)
async def create_attendance(attendance: AttendanceCreate, current_user: AdminUser = Depends(get_current_user)):
    attendance_obj = Attendance(**attendance.model_dump())
    doc = attendance_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.attendance.insert_one(doc)
    return attendance_obj

@api_router.post("/attendance/upload-csv")
async def upload_attendance_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        required_columns = ['roll_number', 'date', 'status']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns}")
        
        records_created = 0
        attendance_date = None
        
        for _, row in df.iterrows():
            # Find student by roll number
            student = await db.students.find_one({"roll_number": str(row['roll_number'])}, {"_id": 0})
            if not student:
                continue
            
            attendance_date = str(row['date'])
            attendance_obj = Attendance(
                student_id=student['id'],
                date=attendance_date,
                status=str(row['status']).lower(),
                subject=str(row.get('subject', '')) if pd.notna(row.get('subject')) else None
            )
            
            doc = attendance_obj.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            
            await db.attendance.insert_one(doc)
            records_created += 1
        
        # Trigger background notification task
        if attendance_date:
            background_tasks.add_task(process_attendance_and_notify, attendance_date)
        
        return {"message": f"Successfully uploaded {records_created} attendance records", "records_created": records_created}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@api_router.get("/attendance", response_model=List[Attendance])
async def get_attendance(date: Optional[str] = None, current_user: AdminUser = Depends(get_current_user)):
    query = {"date": date} if date else {}
    attendance_records = await db.attendance.find(query, {"_id": 0}).to_list(None)
    return attendance_records

@api_router.post("/attendance/trigger-notifications")
async def trigger_notifications(
    background_tasks: BackgroundTasks,
    date: str,
    current_user: AdminUser = Depends(get_current_user)
):
    background_tasks.add_task(process_attendance_and_notify, date)
    return {"message": "Notification processing started"}

# Notification Routes
@api_router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    status: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_user)
):
    query = {"status": status} if status else {}
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).to_list(None)
    return notifications

@api_router.post("/notifications/{notification_id}/retry")
async def retry_notification(
    notification_id: str,
    current_user: AdminUser = Depends(get_current_user)
):
    notification = await db.notifications.find_one({"id": notification_id}, {"_id": 0})
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification['retry_count'] >= 3:
        raise HTTPException(status_code=400, detail="Maximum retry attempts reached")
    
    # Retry sending
    success = False
    result = None
    
    if notification['type'] == 'sms':
        success, result = await send_sms(notification['phone_number'], notification['message'])
    elif notification['type'] == 'voice':
        success, result = await make_voice_call(notification['phone_number'], notification['message'])
    
    # Update notification
    update_data = {
        "status": "sent" if success else "failed",
        "retry_count": notification['retry_count'] + 1,
        "error_message": None if success else result,
        "sent_at": datetime.now(timezone.utc).isoformat() if success else notification.get('sent_at')
    }
    
    await db.notifications.update_one({"id": notification_id}, {"$set": update_data})
    
    return {"message": "Retry successful" if success else "Retry failed", "success": success}

# Voice Template Routes
@api_router.post("/voice-templates", response_model=VoiceTemplate)
async def create_voice_template(template: VoiceTemplateCreate, current_user: AdminUser = Depends(get_current_user)):
    template_obj = VoiceTemplate(**template.model_dump())
    doc = template_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.voice_templates.insert_one(doc)
    return template_obj

@api_router.get("/voice-templates", response_model=List[VoiceTemplate])
async def get_voice_templates(current_user: AdminUser = Depends(get_current_user)):
    templates = await db.voice_templates.find({}, {"_id": 0}).to_list(None)
    return templates

@api_router.put("/voice-templates/{template_id}", response_model=VoiceTemplate)
async def update_voice_template(
    template_id: str,
    template: VoiceTemplateCreate,
    current_user: AdminUser = Depends(get_current_user)
):
    existing = await db.voice_templates.find_one({"id": template_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template.model_dump()
    await db.voice_templates.update_one({"id": template_id}, {"$set": update_data})
    
    updated = await db.voice_templates.find_one({"id": template_id}, {"_id": 0})
    return VoiceTemplate(**updated)

# Dashboard Stats
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: AdminUser = Depends(get_current_user)):
    total_students = await db.students.count_documents({})
    total_parents = await db.parents.count_documents({})
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_absentees = await db.attendance.count_documents({"date": today, "status": "absent"})
    
    notifications_sent_today = await db.notifications.count_documents({
        "created_at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()}
    })
    
    failed_notifications = await db.notifications.count_documents({"status": "failed"})
    
    return DashboardStats(
        total_students=total_students,
        total_parents=total_parents,
        today_absentees=today_absentees,
        notifications_sent_today=notifications_sent_today,
        failed_notifications=failed_notifications
    )

# Reports
@api_router.get("/reports/daily-summary")
async def get_daily_summary(date: str, current_user: AdminUser = Depends(get_current_user)):
    total_records = await db.attendance.count_documents({"date": date})
    present_count = await db.attendance.count_documents({"date": date, "status": "present"})
    absent_count = await db.attendance.count_documents({"date": date, "status": "absent"})
    
    notifications_sent = await db.notifications.count_documents({
        "created_at": {"$regex": f"^{date}"}
    })
    
    return {
        "date": date,
        "total_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "notifications_sent": notifications_sent,
        "attendance_percentage": round((present_count / total_records * 100), 2) if total_records > 0 else 0
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()