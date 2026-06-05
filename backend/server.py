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
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '').strip()
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '').strip()
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER', '').strip()
twilio_client = None
twilio_configured = False

# Initialize Twilio client with validation
if twilio_account_sid and twilio_auth_token and twilio_phone_number:
    try:
        twilio_client = Client(twilio_account_sid, twilio_auth_token)
        twilio_configured = True
        logging.info(f"✓ Twilio client initialized successfully with phone number: {twilio_phone_number}")
    except Exception as e:
        logging.error(f"✗ Failed to initialize Twilio client: {str(e)}")
        twilio_client = None
        twilio_configured = False
else:
    missing = []
    if not twilio_account_sid:
        missing.append("TWILIO_ACCOUNT_SID")
    if not twilio_auth_token:
        missing.append("TWILIO_AUTH_TOKEN")
    if not twilio_phone_number:
        missing.append("TWILIO_PHONE_NUMBER")
    logging.warning(f"⚠ Twilio not configured. Missing: {', '.join(missing)}")

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

class TwilioTestRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number in E.164 format (e.g., +919876543210)")

class TwilioTestResponse(BaseModel):
    twilio_configured: bool
    sms_result: dict
    voice_result: dict
    message: str

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
    """
    Send SMS via Twilio
    
    Args:
        phone_number: Phone number in E.164 format (e.g., +919876543210)
        message: SMS message content
        
    Returns:
        Tuple of (success: bool, result: str)
        - If success: (True, message_sid)
        - If failure: (False, error_message)
    """
    if not twilio_configured or not twilio_client:
        error_msg = "Twilio not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env"
        logging.error(f"SMS Failed: {error_msg}")
        return False, error_msg
    
    try:
        logging.info(f"Attempting to send SMS to {phone_number}")
        
        # Send SMS via Twilio
        message_obj = twilio_client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone_number
        )
        
        logging.info(f"✓ SMS sent successfully to {phone_number}. SID: {message_obj.sid}, Status: {message_obj.status}")
        return True, message_obj.sid
        
    except Exception as e:
        error_msg = f"SMS sending failed: {str(e)}"
        logging.error(f"✗ {error_msg} (to: {phone_number})")
        return False, error_msg

async def make_voice_call(phone_number: str, message: str, language: str = "en-IN") -> tuple[bool, Optional[str]]:
    """
    Make voice call via Twilio with TwiML
    
    Args:
        phone_number: Phone number in E.164 format (e.g., +919876543210)
        message: Voice message content
        language: TwiML language code (default: en-IN for Indian English)
                  Supported: en-IN, hi-IN, ta-IN, te-IN
        
    Returns:
        Tuple of (success: bool, result: str)
        - If success: (True, call_sid)
        - If failure: (False, error_message)
    """
    if not twilio_configured or not twilio_client:
        error_msg = "Twilio not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env"
        logging.error(f"Voice call failed: {error_msg}")
        return False, error_msg
    
    try:
        logging.info(f"Attempting to make voice call to {phone_number} in language: {language}")
        
        # Map language codes to Twilio-supported languages
        language_map = {
            "english": "en-IN",
            "hindi": "hi-IN",
            "tamil": "ta-IN",
            "telugu": "te-IN"
        }
        
        # Get proper language code
        twiml_language = language_map.get(language.lower(), language)
        
        # Escape XML special characters in message
        safe_message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Create TwiML for voice call
        twiml = f'<Response><Say language="{twiml_language}">{safe_message}</Say></Response>'
        
        # Make the call
        call = twilio_client.calls.create(
            twiml=twiml,
            to=phone_number,
            from_=twilio_phone_number
        )
        
        logging.info(f"✓ Voice call initiated successfully to {phone_number}. SID: {call.sid}, Status: {call.status}")
        return True, call.sid
        
    except Exception as e:
        error_msg = f"Voice call failed: {str(e)}"
        logging.error(f"✗ {error_msg} (to: {phone_number})")
        return False, error_msg

async def process_attendance_and_notify(attendance_date: str):
    """
    Background task to process attendance and send notifications
    
    Process:
    1. Find all absent students for the date
    2. For each absent student:
       - Fetch student details
       - Fetch parent details
       - Check for duplicates
       - Send SMS + Voice call
       - Log all actions
    """
    logging.info(f"📋 Processing attendance for {attendance_date}")
    
    try:
        # Get all absent students for the date
        absent_records = await db.attendance.find(
            {"date": attendance_date, "status": "absent"},
            {"_id": 0}
        ).to_list(None)
        
        if not absent_records:
            logging.info(f"No absent students found for date: {attendance_date}")
            return
        
        logging.info(f"Found {len(absent_records)} absent students for date: {attendance_date}")
        
        notifications_sent = 0
        notifications_failed = 0
        
        for record in absent_records:
            try:
                student_id = record.get("student_id")
                subject = record.get("subject", "class")
                
                # Step 1: Find student
                student = await db.students.find_one({"id": student_id}, {"_id": 0})
                if not student:
                    logging.warning(f"❌ Student not found for ID: {student_id}")
                    continue
                
                roll_number = student.get("roll_number")
                student_name = student.get("name")
                logging.info(f"✓ Student found: {roll_number} - {student_name}")
                
                # Step 2: Fetch parent
                parent_id = student.get("parent_id")
                if not parent_id:
                    logging.warning(f"❌ Parent not found: No parent_id for student {roll_number}")
                    continue
                
                parent = await db.parents.find_one({"id": parent_id}, {"_id": 0})
                if not parent:
                    logging.warning(f"❌ Parent not found: ID {parent_id} for student {roll_number}")
                    continue
                
                parent_name = parent.get("name")
                phone_number = parent.get("phone_number", "").strip()
                
                if not phone_number:
                    logging.warning(f"❌ Parent not found: No phone number for parent {parent_name}")
                    continue
                
                logging.info(f"✓ Parent found: {parent_name} - {phone_number}")
                
                # Step 3: Check for duplicate notifications
                existing_notification = await db.notifications.find_one({
                    "student_id": student_id,
                    "created_at": {"$regex": f"^{attendance_date}"},
                    "message": {"$regex": subject}
                })
                
                if existing_notification:
                    logging.info(f"⚠️  Notification already sent for {student_name} ({subject}) on {attendance_date}, skipping")
                    continue
                
                # Step 4: Create message (STRICT FORMAT)
                message = f"Your ward is absent for {subject} on {attendance_date}"
                
                logging.info(f"📤 Sending notification to {phone_number}...")
                
                # Step 5: Send SMS
                sms_success, sms_result = await send_sms(phone_number, message)
                
                sms_notification = {
                    "id": str(uuid.uuid4()),
                    "student_id": student_id,
                    "parent_id": parent_id,
                    "type": "sms",
                    "status": "sent" if sms_success else "failed",
                    "message": message,
                    "phone_number": phone_number,
                    "retry_count": 0,
                    "error_message": None if sms_success else sms_result,
                    "sent_at": datetime.now(timezone.utc).isoformat() if sms_success else None,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.notifications.insert_one(sms_notification)
                
                if sms_success:
                    logging.info(f"✓ SMS sent successfully to {phone_number}")
                    notifications_sent += 1
                else:
                    logging.error(f"✗ SMS failed: {sms_result}")
                    notifications_failed += 1
                
                # Small delay before voice call
                await asyncio.sleep(2)
                
                # Step 6: Make voice call
                parent_language = parent.get("preferred_language", "english")
                voice_success, voice_result = await make_voice_call(
                    phone_number, 
                    message, 
                    parent_language
                )
                
                voice_notification = {
                    "id": str(uuid.uuid4()),
                    "student_id": student_id,
                    "parent_id": parent_id,
                    "type": "voice",
                    "status": "sent" if voice_success else "failed",
                    "message": message,
                    "phone_number": phone_number,
                    "retry_count": 0,
                    "error_message": None if voice_success else voice_result,
                    "sent_at": datetime.now(timezone.utc).isoformat() if voice_success else None,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.notifications.insert_one(voice_notification)
                
                if voice_success:
                    logging.info(f"✓ Voice call sent successfully to {phone_number}")
                    notifications_sent += 1
                else:
                    logging.error(f"✗ Voice call failed: {voice_result}")
                    notifications_failed += 1
                
            except Exception as e:
                logging.error(f"Error processing notification for student {record.get('student_id', 'unknown')}: {str(e)}")
                notifications_failed += 1
                continue
        
        logging.info(f"✅ Notification processing complete for {attendance_date}: {notifications_sent} sent, {notifications_failed} failed")
        
    except Exception as e:
        logging.error(f"Critical error in process_attendance_and_notify: {str(e)}")
        raise
        logging.error(f"Critical error in process_attendance_and_notify: {str(e)}")
        raise

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
async def create_attendance(
    attendance: AttendanceCreate,
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Create a single attendance record
    
    If status is 'absent', notifications will be triggered automatically
    """
    # Validate student exists
    student = await db.students.find_one({"id": attendance.student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    attendance_obj = Attendance(**attendance.model_dump())
    doc = attendance_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.attendance.insert_one(doc)
    
    # If student is absent, trigger notification
    if attendance.status.lower() == 'absent':
        logging.info(f"Triggering notification for absent student: {student['name']} on {attendance.date}")
        background_tasks.add_task(process_attendance_and_notify, attendance.date)
    
    return attendance_obj

@api_router.post("/attendance/upload-csv")
async def upload_attendance_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Upload attendance CSV file and trigger notifications for absent students
    
    CSV Format:
    - Required columns: roll_number, date, status, subject
    - Status normalization:
      - absent, a, 0, false → ABSENT
      - present, p, 1, true → PRESENT
    
    Returns:
    {
        "status": "success",
        "total_records": X,
        "absent_count": X,
        "notifications_sent": X,
        "failed": X,
        "skipped": X
    }
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['roll_number', 'date', 'status', 'subject']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain columns: {required_columns}"
            )
        
        total_records = 0
        absent_count = 0
        present_count = 0
        skipped_count = 0
        attendance_date = None
        
        logging.info(f"📄 Processing CSV upload with {len(df)} rows by user: {current_user.email}")
        
        for index, row in df.iterrows():
            try:
                # Extract and normalize data
                roll_number = str(row['roll_number']).strip()
                date_str = str(row['date']).strip()
                status_raw = str(row['status']).strip().lower()
                subject = str(row['subject']).strip() if pd.notna(row.get('subject')) else "class"
                
                # Set attendance date (use first valid date)
                if not attendance_date:
                    attendance_date = date_str
                
                logging.info(f"📋 Processing attendance for {date_str}")
                
                # Step 1: Find student by roll number
                student = await db.students.find_one({"roll_number": roll_number}, {"_id": 0})
                
                if not student:
                    logging.warning(f"❌ Student not found: {roll_number}")
                    skipped_count += 1
                    continue
                
                logging.info(f"✓ Student found: {roll_number}")
                
                # Step 2: Normalize status
                if status_raw in ['absent', 'a', '0', 'false']:
                    status = 'absent'
                    absent_count += 1
                elif status_raw in ['present', 'p', '1', 'true']:
                    status = 'present'
                    present_count += 1
                    logging.info(f"⏭️  Skipped present student: {roll_number}")
                else:
                    logging.warning(f"❌ Unknown status '{status_raw}' for roll {roll_number}, skipping")
                    skipped_count += 1
                    continue
                
                # Step 3: Create attendance record
                attendance_obj = Attendance(
                    student_id=student['id'],
                    date=date_str,
                    status=status,
                    subject=subject
                )
                
                doc = attendance_obj.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                
                await db.attendance.insert_one(doc)
                total_records += 1
                
                logging.debug(f"✓ Attendance record created: {student['name']} ({roll_number}) - {status} - {subject} on {date_str}")
                
            except Exception as e:
                logging.error(f"Error processing row {index}: {str(e)}")
                skipped_count += 1
                continue
        
        # Step 4: Trigger background notification task ONLY for absent students
        if attendance_date and absent_count > 0:
            logging.info(f"📤 Triggering notifications for {absent_count} absent students on {attendance_date}")
            background_tasks.add_task(process_attendance_and_notify, attendance_date)
            notifications_triggered = True
        else:
            logging.info(f"No absent students found, notifications not triggered")
            notifications_triggered = False
        
        # Step 5: Return detailed response
        response = {
            "status": "success",
            "total_records": total_records,
            "absent_count": absent_count,
            "present_count": present_count,
            "notifications_sent": absent_count if notifications_triggered else 0,
            "failed": 0,  # Will be updated by background task
            "skipped": skipped_count,
            "date": attendance_date,
            "notifications_triggered": notifications_triggered
        }
        
        logging.info(f"✅ CSV upload complete: {total_records} created, {absent_count} absent, {present_count} present, {skipped_count} skipped")
        
        return response
    
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
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

@api_router.get("/notifications/stats")
async def get_notification_stats(
    date: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Get notification statistics
    
    Optional date parameter to filter by specific date (YYYY-MM-DD)
    """
    query = {}
    if date:
        query["created_at"] = {"$regex": f"^{date}"}
    
    total_notifications = await db.notifications.count_documents(query)
    sent_notifications = await db.notifications.count_documents({**query, "status": "sent"})
    failed_notifications = await db.notifications.count_documents({**query, "status": "failed"})
    
    sms_count = await db.notifications.count_documents({**query, "type": "sms"})
    voice_count = await db.notifications.count_documents({**query, "type": "voice"})
    
    sms_sent = await db.notifications.count_documents({**query, "type": "sms", "status": "sent"})
    voice_sent = await db.notifications.count_documents({**query, "type": "voice", "status": "sent"})
    
    return {
        "date": date if date else "all_time",
        "total_notifications": total_notifications,
        "sent": sent_notifications,
        "failed": failed_notifications,
        "success_rate": round((sent_notifications / total_notifications * 100), 2) if total_notifications > 0 else 0,
        "by_type": {
            "sms": {
                "total": sms_count,
                "sent": sms_sent,
                "failed": sms_count - sms_sent
            },
            "voice": {
                "total": voice_count,
                "sent": voice_sent,
                "failed": voice_count - voice_sent
            }
        }
    }

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

# Twilio Test Endpoint
@api_router.post("/test/twilio", response_model=TwilioTestResponse)
async def test_twilio_integration(
    request: TwilioTestRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Test Twilio SMS and Voice Call Integration
    
    This endpoint sends a test SMS and makes a test voice call to verify Twilio configuration.
    
    **Required:** Phone number in E.164 format (e.g., +919876543210)
    
    **Note:** For Twilio trial accounts, the phone number must be verified in Twilio Console.
    """
    logging.info(f"Twilio test requested by {current_user.email} for phone: {request.phone_number}")
    
    # Check if Twilio is configured
    if not twilio_configured:
        return TwilioTestResponse(
            twilio_configured=False,
            sms_result={
                "success": False,
                "error": "Twilio not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in backend/.env"
            },
            voice_result={
                "success": False,
                "error": "Twilio not configured"
            },
            message="Twilio credentials are missing. Please configure them in backend/.env file."
        )
    
    # Test SMS
    sms_message = f"Hello! This is a test SMS from MLR Institute Auto-Call System. Sent at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC."
    sms_success, sms_result = await send_sms(request.phone_number, sms_message)
    
    # Wait 2 seconds before voice call
    await asyncio.sleep(2)
    
    # Test Voice Call
    voice_message = "Hello! This is a test call from M L R Institute Auto-Call Notification System. If you can hear this message, your Twilio integration is working correctly."
    voice_success, voice_result = await make_voice_call(request.phone_number, voice_message, "en-IN")
    
    # Prepare response
    response_message = ""
    if sms_success and voice_success:
        response_message = "✓ Both SMS and voice call sent successfully! Check your phone."
    elif sms_success:
        response_message = "✓ SMS sent successfully, but voice call failed. Check logs for details."
    elif voice_success:
        response_message = "✓ Voice call sent successfully, but SMS failed. Check logs for details."
    else:
        response_message = "✗ Both SMS and voice call failed. Check Twilio credentials and phone number format."
    
    return TwilioTestResponse(
        twilio_configured=True,
        sms_result={
            "success": sms_success,
            "message_sid": sms_result if sms_success else None,
            "error": sms_result if not sms_success else None
        },
        voice_result={
            "success": voice_success,
            "call_sid": voice_result if voice_success else None,
            "error": voice_result if not voice_success else None
        },
        message=response_message
    )

@api_router.get("/test/twilio-status")
async def get_twilio_status(current_user: AdminUser = Depends(get_current_user)):
    """
    Check Twilio configuration status without sending any messages
    """
    return {
        "configured": twilio_configured,
        "account_sid": twilio_account_sid[:10] + "..." if twilio_account_sid else None,
        "phone_number": twilio_phone_number if twilio_phone_number else None,
        "message": "Twilio is configured and ready" if twilio_configured else "Twilio is not configured. Please set credentials in .env"
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