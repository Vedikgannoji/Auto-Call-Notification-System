# Quick Reference Card

**MLR Institute Auto-Call Notification System**  
**Version:** 1.0.0 | **Status:** ✅ Production Ready

---

## 🚀 Quick Start (3 Steps)

### 1. Start Backend
```bash
cd backend
venv\Scripts\activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Start Frontend
```bash
cd frontend
yarn start
```

### 3. Login
- URL: http://localhost:3000
- Email: admin@mlrit.ac.in
- Password: admin123

---

## 📋 Daily Workflow

### Upload Attendance (3 Steps)

1. **Create CSV**
   ```csv
   roll_number,date,status,subject
   2021001,31-03-2026,absent,Math
   ```

2. **Upload**
   - Attendance → Upload CSV → Select File → Upload

3. **Verify**
   - Notifications → Check status

---

## 📱 Phone Number Format

✅ **Correct:** `+919876543210`  
❌ **Wrong:** `9876543210`, `+91 9876543210`, `919876543210`

---

## 📊 Status Formats

### Absent (Sends Notification)
- `absent`, `a`, `0`, `false`

### Present (Skips Notification)
- `present`, `p`, `1`, `true`

---

## 💬 Message Format

```
Your ward is absent for {subject} on {date}
```

**Example:**
```
Your ward is absent for Mathematics on 31-03-2026
```

---

## 🔧 Common Commands

### Backend
```bash
# Start
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Create admin
python seed_admin.py

# Test
python test_final_system.py
```

### Frontend
```bash
# Install
yarn install

# Start
yarn start

# Build
yarn build
```

### MongoDB
```bash
# Start
net start MongoDB

# Connect
mongo

# Use database
use auto_call_notification_db
```

---

## 📁 Key Files

### Backend
- `backend/server.py` - Main API (1000+ lines)
- `backend/requirements.txt` - Dependencies (30 packages)
- `backend/.env` - Configuration
- `backend/seed_admin.py` - Create admin

### Frontend
- `frontend/src/App.js` - Main app
- `frontend/src/pages/` - 8 pages
- `frontend/.env` - Configuration

### Tests
- `test_final_system.py` - Complete test
- `sample_attendance.csv` - Sample data

---

## 🔐 Environment Variables

### Backend (.env)
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="auto_call_notification_db"
JWT_SECRET="your-secret-key"
TWILIO_ACCOUNT_SID="ACxxx..."
TWILIO_AUTH_TOKEN="xxx..."
TWILIO_PHONE_NUMBER="+1234567890"
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🎯 API Endpoints (Quick List)

### Auth
- POST `/api/auth/login`
- GET `/api/auth/me`

### Students
- GET `/api/students`
- POST `/api/students`

### Parents
- GET `/api/parents`
- POST `/api/parents`

### Attendance
- POST `/api/attendance/upload-csv`
- GET `/api/attendance`

### Notifications
- GET `/api/notifications`
- GET `/api/notifications/stats`

### Testing
- POST `/api/test/twilio`
- GET `/api/test/twilio-status`

---

## 🐛 Quick Troubleshooting

### Backend won't start
```bash
# Check if port is in use
netstat -ano | findstr :8001

# Kill process
taskkill /PID <PID> /F
```

### MongoDB not running
```bash
net start MongoDB
```

### Login failed
```bash
cd backend
python seed_admin.py
```

### Notifications not sending
1. Check Twilio credentials in `.env`
2. Check phone number format (+91...)
3. Check backend logs for errors

---

## 📚 Documentation Quick Links

### For Daily Use
- `DAILY_OPERATIONS_GUIDE.md` - Complete daily guide
- `QUICKSTART.md` - Getting started

### For Setup
- `README.md` - System overview
- `DEPLOYMENT_CHECKLIST.md` - Production deployment

### For Features
- `FINAL_ATTENDANCE_SYSTEM.md` - Attendance system
- `TWILIO_SETUP.md` - Twilio configuration

### For Status
- `SYSTEM_STATUS.md` - Current status
- `PROJECT_HANDOVER.md` - Complete handover

---

## ✅ Pre-Upload Checklist

Before uploading attendance CSV:
- [ ] CSV has 4 columns: roll_number, date, status, subject
- [ ] Date format is DD-MM-YYYY
- [ ] All students exist in database
- [ ] All students have parent_id
- [ ] All parents have phone numbers
- [ ] Phone numbers are in E.164 format

---

## 📊 Response Format

```json
{
  "status": "success",
  "total_records": 10,
  "absent_count": 3,
  "present_count": 7,
  "notifications_sent": 3,
  "failed": 0,
  "skipped": 0
}
```

---

## 🎨 Emoji Legend

- 📋 Processing
- ✓ Success
- ❌ Error
- ⚠️ Warning
- 📤 Sending
- ✅ Complete
- ⏭️ Skipped

---

## 💡 Pro Tips

1. Test with 1-2 students first
2. Use your own phone for testing
3. Check logs for detailed info
4. Keep backend terminal visible
5. Bookmark this page!

---

## 🆘 Emergency Contacts

### System Issues
- Check: `SYSTEM_STATUS.md`
- Check: `TECHNICAL_ANALYSIS_REPORT.md`

### Twilio Issues
- Check: `TWILIO_TESTING_GUIDE.md`
- Twilio Console: https://console.twilio.com

### Database Issues
- Check: MongoDB logs
- Verify connection string

---

## 📈 System Capacity

- **Students:** 1000+
- **Processing:** ~5 sec/student
- **Suitable For:** 100 absent students/batch
- **Delay:** 2 sec between SMS/Call

---

## 🔄 Update Cycle

### Daily
- Upload attendance
- Check notifications
- Verify dashboard

### Weekly
- Review reports
- Check failed notifications
- Update data if needed

### Monthly
- Generate monthly report
- Archive old data
- Check Twilio usage

---

## 🎯 Success Metrics

- ✅ CSV uploads successfully
- ✅ Notifications sent automatically
- ✅ Message format correct
- ✅ Dashboard shows statistics
- ✅ Reports generate correctly

---

## 📞 Default Credentials

**⚠️ CHANGE IN PRODUCTION**

```
Email: admin@mlrit.ac.in
Password: admin123
```

---

## 🚀 Production Checklist

- [ ] Change admin password
- [ ] Update JWT secret
- [ ] Configure Twilio production account
- [ ] Set up MongoDB Atlas
- [ ] Enable HTTPS
- [ ] Configure backups
- [ ] Set up monitoring

---

**Quick Reference v1.0**  
**Last Updated:** March 31, 2026

**Need more details?** See full documentation files.
