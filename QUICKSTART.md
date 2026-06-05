# Quick Start Guide - MLR Institute Auto-Call System

## Prerequisites

Before running the app, ensure you have:
- **Python 3.11+** installed
- **Node.js 18+** and **Yarn** installed
- **MongoDB** running (locally or remote)
- **Git** (if cloning)

---

## Step 1: Start MongoDB

### Option A: Local MongoDB
```bash
# Windows (if MongoDB is installed as service)
net start MongoDB

# Or start manually
mongod --dbpath C:\data\db
```

### Option B: MongoDB Atlas (Cloud)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Get connection string
4. Update `backend/.env` with your connection string

---

## Step 2: Backend Setup

### 2.1 Navigate to backend directory
```bash
cd backend
```

### 2.2 Create Python virtual environment (recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 2.3 Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Configure environment variables
The `backend/.env` file should already exist. Verify it has:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="auto_call_notification_db"
CORS_ORIGINS="*"
JWT_SECRET="your-secret-key-change-in-production-12345"
TWILIO_ACCOUNT_SID=""
TWILIO_AUTH_TOKEN=""
TWILIO_PHONE_NUMBER=""
```

**Note:** Twilio credentials are optional for initial testing. The app will work without them, but notifications won't be sent.

### 2.5 Seed the database with admin user
```bash
python seed_admin.py
```

You should see:
```
✓ Admin user created successfully!
  Email: admin@mlrit.ac.in
  Password: admin123
```

### 2.6 Start the backend server
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

**Keep this terminal open!**

---

## Step 3: Frontend Setup

### 3.1 Open a NEW terminal and navigate to frontend
```bash
cd frontend
```

### 3.2 Install dependencies
```bash
yarn install
```

This will take a few minutes to download all packages.

### 3.3 Verify environment configuration
Check `frontend/.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

**Important:** Change the backend URL to local:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3.4 Start the frontend development server
```bash
yarn start
```

The app will automatically open in your browser at `http://localhost:3000`

---

## Step 4: Login to the App

1. Browser should open automatically to `http://localhost:3000`
2. You'll see the login page
3. Use these credentials:
   - **Email:** `admin@mlrit.ac.in`
   - **Password:** `admin123`
4. Click "Sign In"

You should now see the Dashboard!

---

## Troubleshooting

### Backend won't start

**Error: "ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate

# Then reinstall
pip install -r requirements.txt
```

**Error: "MongoDB connection failed"**
```bash
# Check if MongoDB is running
# Windows:
net start MongoDB

# Or check the service in Task Manager
```

**Error: "Port 8001 already in use"**
```bash
# Find and kill the process using port 8001
# Windows:
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Or use a different port:
uvicorn server:app --host 0.0.0.0 --port 8002 --reload
# Then update frontend/.env to use port 8002
```

### Frontend won't start

**Error: "yarn: command not found"**
```bash
# Install yarn globally
npm install -g yarn

# Then try again
yarn install
```

**Error: "Port 3000 already in use"**
```bash
# The app will ask if you want to use a different port
# Type 'y' and press Enter
```

**Error: "Cannot connect to backend"**
- Make sure backend is running on port 8001
- Check `frontend/.env` has correct backend URL
- Try accessing `http://localhost:8001/api/auth/me` in browser (should show 401 error - that's OK)

### Login doesn't work

**Error: "Invalid credentials"**
```bash
# Re-run the seed script
cd backend
python seed_admin.py
```

**Error: "Network Error"**
- Backend is not running
- Check backend terminal for errors
- Verify backend URL in frontend/.env

---

## Quick Test Checklist

Once logged in, test these features:

1. **Dashboard** - Should show 0 students, 0 parents
2. **Parents** - Click "Add Parent" and create a test parent
3. **Students** - Click "Add Student" and create a test student (link to parent)
4. **Attendance** - Try uploading the `sample_attendance.csv` file
5. **Notifications** - Check if any notifications were created (will fail without Twilio)
6. **Reports** - Generate a report for today's date
7. **Settings** - View voice templates

---

## Optional: Configure Twilio (for SMS/Voice)

If you want to test notifications:

1. Sign up at https://www.twilio.com/ (free trial)
2. Get your credentials from Twilio Console
3. Update `backend/.env`:
```env
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token"
TWILIO_PHONE_NUMBER="+1234567890"
```
4. Restart backend server (Ctrl+C, then run uvicorn again)
5. Upload attendance CSV with absent students
6. Check Notifications page for sent messages

---

## Stopping the App

### Stop Frontend
- Press `Ctrl+C` in the frontend terminal

### Stop Backend
- Press `Ctrl+C` in the backend terminal
- Deactivate virtual environment: `deactivate`

### Stop MongoDB (if running manually)
- Press `Ctrl+C` in MongoDB terminal

---

## Next Steps

- Read `TECHNICAL_ANALYSIS_REPORT.md` for detailed system analysis
- Check `TWILIO_SETUP.md` for Twilio configuration guide
- Review `ARCHITECTURE.md` for system architecture details

---

## Need Help?

Common issues:
- **MongoDB not installed?** Download from https://www.mongodb.com/try/download/community
- **Python not installed?** Download from https://www.python.org/downloads/
- **Node.js not installed?** Download from https://nodejs.org/

For detailed troubleshooting, check the TECHNICAL_ANALYSIS_REPORT.md file.
