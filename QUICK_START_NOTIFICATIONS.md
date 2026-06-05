# Attendance Notifications - Quick Start

## 🚀 5-Minute Setup

### Step 1: Ensure Prerequisites (1 min)

✅ Backend running  
✅ MongoDB connected  
✅ Twilio configured (optional for testing)  
✅ At least one parent with phone number  
✅ At least one student linked to parent  

---

### Step 2: Create Test CSV (1 min)

Create `test_attendance.csv`:
```csv
roll_number,date,status,subject
YOUR_STUDENT_ROLL,2026-03-31,absent,Mathematics
```

Replace `YOUR_STUDENT_ROLL` with actual roll number from database.

---

### Step 3: Upload CSV (1 min)

**Via Swagger UI:**
1. Go to http://localhost:8001/docs
2. Login and authorize
3. Find `POST /api/attendance/upload-csv`
4. Upload your CSV file
5. Click Execute

**Via cURL:**
```bash
curl -X POST "http://localhost:8001/api/attendance/upload-csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_attendance.csv"
```

---

### Step 4: Check Results (2 min)

**Check Logs:**
```
INFO:root:Starting notification processing for date: 2026-03-31
INFO:root:Found 1 absent students for date: 2026-03-31
INFO:root:✓ SMS sent successfully to +919876543210
INFO:root:✓ Voice call initiated successfully to +919876543210
INFO:root:Notification processing complete: 2 sent, 0 failed
```

**Check Phone:**
- SMS should arrive within 10 seconds
- Voice call should arrive within 15 seconds

**Check Database:**
```bash
curl -X GET "http://localhost:8001/api/notifications" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Quick Commands

### Check Statistics
```bash
curl -X GET "http://localhost:8001/api/notifications/stats?date=2026-03-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check Failed Notifications
```bash
curl -X GET "http://localhost:8001/api/notifications?status=failed" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Retry Failed Notification
```bash
curl -X POST "http://localhost:8001/api/notifications/{id}/retry" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Manual Trigger
```bash
curl -X POST "http://localhost:8001/api/attendance/trigger-notifications?date=2026-03-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Success Indicators

You'll know it's working when:
- ✅ CSV upload returns `"notifications_triggered": true`
- ✅ Backend logs show "✓ SMS sent successfully"
- ✅ Backend logs show "✓ Voice call initiated successfully"
- ✅ Phone receives SMS
- ✅ Phone receives voice call
- ✅ Notifications appear in database

---

## 🚨 Quick Troubleshooting

### No notifications sent?
→ Check if students have parent_id  
→ Check if parents have phone_number  
→ Check backend logs for errors

### Notifications failed?
→ Check Twilio credentials  
→ Check phone number format (+919876543210)  
→ Check Twilio Console logs

### Duplicate notifications?
→ System prevents duplicates automatically  
→ Check logs for "already sent" messages

---

## 📖 Full Documentation

- **Complete Guide:** `ATTENDANCE_NOTIFICATION_GUIDE.md`
- **Technical Details:** `ATTENDANCE_NOTIFICATION_CHANGES.md`
- **Test Script:** `test_attendance_notifications.py`

---

## 🎯 Status Formats

The system accepts multiple formats:

**Absent:**
- `absent`, `a`, `0`, `false`, `no`

**Present:**
- `present`, `p`, `1`, `true`, `yes`

---

**That's it!** Your attendance notification system is ready to use! 🎉
