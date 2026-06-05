# Attendance Notification System - Complete Guide

## 🎯 Overview

The attendance notification system automatically sends SMS and voice call notifications to parents when their children are marked absent.

---

## 🔄 How It Works

### Flow Diagram

```
CSV Upload / API Call
        ↓
Parse Attendance Data
        ↓
Identify Absent Students (status = 'absent', '0', 'a', 'false')
        ↓
For Each Absent Student:
        ↓
    Fetch Student Details
        ↓
    Fetch Parent Contact Info
        ↓
    Check for Duplicate Notifications
        ↓
    Get Voice Template (based on language)
        ↓
    Send SMS Notification
        ↓
    Wait 2 seconds
        ↓
    Make Voice Call
        ↓
    Log Both Notifications to Database
        ↓
Complete Processing
```

---

## 📊 Features Implemented

### ✅ Core Features

1. **Automatic Notification Triggering**
   - Triggered automatically after CSV upload
   - Triggered automatically when creating absent attendance via API
   - Can be manually triggered for any date

2. **Smart Status Parsing**
   - Accepts multiple status formats:
     - `absent`, `a`, `0`, `false`, `no` → Absent
     - `present`, `p`, `1`, `true`, `yes` → Present

3. **Duplicate Prevention**
   - Checks if notification already sent for student on same date
   - Prevents multiple notifications for same absence

4. **Error Handling**
   - Handles missing students gracefully
   - Handles missing parents gracefully
   - Handles missing phone numbers
   - Handles Twilio failures
   - Logs all errors for debugging

5. **Multi-Language Support**
   - Uses parent's preferred language for voice calls
   - Supports: English, Hindi, Tamil, Telugu

6. **Comprehensive Logging**
   - Logs every step of the process
   - Tracks success/failure counts
   - Provides detailed error messages

---

## 🚀 API Endpoints

### 1. Upload Attendance CSV

**Endpoint:** `POST /api/attendance/upload-csv`

**Description:** Upload CSV file with attendance data. Automatically triggers notifications for absent students.

**Request:**
```bash
curl -X POST "http://localhost:8001/api/attendance/upload-csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@attendance.csv"
```

**CSV Format:**
```csv
roll_number,date,status,subject
2021001,2026-03-31,present,Mathematics
2021002,2026-03-31,absent,Mathematics
2021003,2026-03-31,0,Physics
2021004,2026-03-31,1,Physics
```

**Status Values:**
- Absent: `absent`, `a`, `0`, `false`, `no`
- Present: `present`, `p`, `1`, `true`, `yes`

**Response:**
```json
{
  "message": "Successfully uploaded 4 attendance records",
  "records_created": 4,
  "records_skipped": 0,
  "date": "2026-03-31",
  "notifications_triggered": true
}
```

---

### 2. Create Single Attendance Record

**Endpoint:** `POST /api/attendance`

**Description:** Create a single attendance record. Automatically triggers notification if status is 'absent'.

**Request:**
```bash
curl -X POST "http://localhost:8001/api/attendance" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student-uuid-here",
    "date": "2026-03-31",
    "status": "absent",
    "subject": "Mathematics"
  }'
```

**Response:**
```json
{
  "id": "notification-uuid",
  "student_id": "student-uuid",
  "date": "2026-03-31",
  "status": "absent",
  "subject": "Mathematics",
  "created_at": "2026-03-31T10:30:00Z"
}
```

---

### 3. Manually Trigger Notifications

**Endpoint:** `POST /api/attendance/trigger-notifications`

**Description:** Manually trigger notifications for a specific date (useful for re-sending or testing).

**Request:**
```bash
curl -X POST "http://localhost:8001/api/attendance/trigger-notifications?date=2026-03-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "message": "Notification processing started"
}
```

---

### 4. Get Notifications

**Endpoint:** `GET /api/notifications`

**Description:** Get all notifications, optionally filtered by status.

**Request:**
```bash
# Get all notifications
curl -X GET "http://localhost:8001/api/notifications" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only failed notifications
curl -X GET "http://localhost:8001/api/notifications?status=failed" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": "notification-uuid",
    "student_id": "student-uuid",
    "parent_id": "parent-uuid",
    "type": "sms",
    "status": "sent",
    "message": "Dear Parent, your child was absent...",
    "phone_number": "+919876543210",
    "retry_count": 0,
    "error_message": null,
    "sent_at": "2026-03-31T10:30:00Z",
    "created_at": "2026-03-31T10:30:00Z"
  }
]
```

---

### 5. Get Notification Statistics

**Endpoint:** `GET /api/notifications/stats`

**Description:** Get notification statistics, optionally for a specific date.

**Request:**
```bash
# Get all-time stats
curl -X GET "http://localhost:8001/api/notifications/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get stats for specific date
curl -X GET "http://localhost:8001/api/notifications/stats?date=2026-03-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "date": "2026-03-31",
  "total_notifications": 10,
  "sent": 8,
  "failed": 2,
  "success_rate": 80.0,
  "by_type": {
    "sms": {
      "total": 5,
      "sent": 4,
      "failed": 1
    },
    "voice": {
      "total": 5,
      "sent": 4,
      "failed": 1
    }
  }
}
```

---

### 6. Retry Failed Notification

**Endpoint:** `POST /api/notifications/{notification_id}/retry`

**Description:** Retry a failed notification (max 3 attempts).

**Request:**
```bash
curl -X POST "http://localhost:8001/api/notifications/abc-123/retry" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "message": "Retry successful",
  "success": true
}
```

---

## 🧪 End-to-End Testing

### Test Scenario 1: CSV Upload with Absent Students

**Step 1: Create Test Data**

1. Create a parent:
```bash
curl -X POST "http://localhost:8001/api/parents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Parent",
    "phone_number": "+919876543210",
    "email": "parent@test.com",
    "relationship": "parent",
    "preferred_language": "english"
  }'
```

2. Create a student linked to parent:
```bash
curl -X POST "http://localhost:8001/api/students" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "TEST001",
    "name": "Test Student",
    "email": "student@test.com",
    "department": "Computer Science",
    "year": 1,
    "parent_id": "PARENT_ID_FROM_STEP_1"
  }'
```

**Step 2: Create CSV File**

Create `test_attendance.csv`:
```csv
roll_number,date,status,subject
TEST001,2026-03-31,absent,Mathematics
```

**Step 3: Upload CSV**

```bash
curl -X POST "http://localhost:8001/api/attendance/upload-csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_attendance.csv"
```

**Step 4: Verify Notifications**

1. Check backend logs:
```
INFO:root:Processing CSV upload with 1 rows by user: admin@mlrit.ac.in
INFO:root:Triggering notifications for date: 2026-03-31
INFO:root:Starting notification processing for date: 2026-03-31
INFO:root:Found 1 absent students for date: 2026-03-31
INFO:root:Processing notifications for student: Test Student (Roll: TEST001)
INFO:root:Attempting to send SMS to +919876543210
INFO:root:✓ SMS sent successfully to +919876543210. SID: SMxxxx
INFO:root:Attempting to make voice call to +919876543210 in language: english
INFO:root:✓ Voice call initiated successfully to +919876543210. SID: CAxxxx
INFO:root:✓ Notifications processed for Test Student: SMS=True, Voice=True
INFO:root:Notification processing complete for 2026-03-31: 2 sent, 0 failed
```

2. Check your phone for SMS and voice call

3. Check notifications in database:
```bash
curl -X GET "http://localhost:8001/api/notifications?status=sent" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

4. Check notification stats:
```bash
curl -X GET "http://localhost:8001/api/notifications/stats?date=2026-03-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Test Scenario 2: Different Status Formats

Create CSV with various status formats:
```csv
roll_number,date,status,subject
TEST001,2026-03-31,absent,Math
TEST002,2026-03-31,0,Math
TEST003,2026-03-31,a,Math
TEST004,2026-03-31,false,Math
TEST005,2026-03-31,present,Math
TEST006,2026-03-31,1,Math
TEST007,2026-03-31,p,Math
```

Upload and verify:
- Only TEST001, TEST002, TEST003, TEST004 trigger notifications
- TEST005, TEST006, TEST007 are marked present (no notifications)

---

### Test Scenario 3: Duplicate Prevention

1. Upload attendance CSV for date 2026-03-31
2. Wait for notifications to complete
3. Upload same CSV again
4. Check logs - should see "Notification already sent" messages
5. Verify no duplicate notifications in database

---

### Test Scenario 4: Error Handling

**Test Missing Student:**
```csv
roll_number,date,status,subject
NONEXISTENT,2026-03-31,absent,Math
```
- Should skip with warning in logs
- No notification sent

**Test Missing Parent:**
1. Create student without parent_id
2. Upload attendance marking them absent
3. Should skip with warning in logs

**Test Missing Phone Number:**
1. Create parent without phone_number
2. Create student linked to that parent
3. Upload attendance marking them absent
4. Should skip with warning in logs

---

## 📋 Database Schema

### Notifications Collection

```javascript
{
  "id": "uuid",
  "student_id": "uuid",
  "parent_id": "uuid",
  "type": "sms" | "voice",
  "status": "sent" | "failed",
  "message": "notification message",
  "phone_number": "+919876543210",
  "retry_count": 0,
  "error_message": null | "error details",
  "sent_at": "2026-03-31T10:30:00Z" | null,
  "created_at": "2026-03-31T10:30:00Z"
}
```

---

## 🔍 Monitoring & Debugging

### Check Backend Logs

```bash
# Watch logs in real-time
tail -f backend.log

# Or if running in terminal
# Logs will appear in console
```

### Key Log Messages

**Success:**
```
✓ SMS sent successfully to +919876543210. SID: SMxxxx
✓ Voice call initiated successfully to +919876543210. SID: CAxxxx
✓ Notifications processed for Test Student: SMS=True, Voice=True
```

**Warnings:**
```
Student not found for roll number: TEST999
Parent not found for student: Test Student (ID: xxx)
No phone number for parent: Test Parent (ID: xxx)
Notification already sent for student Test Student on 2026-03-31, skipping
```

**Errors:**
```
✗ SMS sending failed: Unable to create record: The 'To' number...
✗ Voice call failed: Unable to create record...
Error processing notification for student xxx: ...
```

---

## 🎯 Best Practices

### 1. CSV Format
- Always include required columns: `roll_number`, `date`, `status`
- Use consistent date format: `YYYY-MM-DD`
- Use clear status values: `present` or `absent`

### 2. Testing
- Test with verified phone numbers first (Twilio trial)
- Start with small CSV files (5-10 students)
- Monitor logs during testing
- Check notification stats after each test

### 3. Production
- Ensure all students have valid parent links
- Ensure all parents have valid phone numbers
- Monitor notification success rates
- Set up alerts for high failure rates

### 4. Error Recovery
- Check failed notifications regularly
- Use retry endpoint for failed notifications
- Investigate error messages
- Fix data issues (missing parents, invalid phones)

---

## 🚨 Troubleshooting

### Issue: No notifications sent

**Check:**
1. Are there absent students in the CSV?
2. Do students exist in database?
3. Do students have parent_id?
4. Do parents have phone numbers?
5. Is Twilio configured?

**Solution:**
```bash
# Check attendance records
curl -X GET "http://localhost:8001/api/attendance?date=2026-03-31" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check notification stats
curl -X GET "http://localhost:8001/api/notifications/stats?date=2026-03-31" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check backend logs for errors
```

---

### Issue: Notifications marked as failed

**Check:**
1. Twilio credentials configured?
2. Phone number in E.164 format?
3. Phone number verified (trial accounts)?
4. Sufficient Twilio credit?

**Solution:**
```bash
# Check Twilio status
curl -X GET "http://localhost:8001/api/test/twilio-status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check failed notifications
curl -X GET "http://localhost:8001/api/notifications?status=failed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Retry failed notification
curl -X POST "http://localhost:8001/api/notifications/{id}/retry" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Issue: Duplicate notifications

**Check:**
1. Are you uploading same CSV multiple times?
2. Are you manually triggering notifications?

**Solution:**
- System prevents duplicates automatically
- Check logs for "Notification already sent" messages
- If duplicates still occur, check created_at timestamps

---

## 📊 Performance Considerations

### Current Implementation
- Sequential processing (one student at a time)
- 2-second delay between SMS and voice call
- Suitable for up to 100 absent students

### For Large Scale (500+ students)
- Consider implementing Celery for parallel processing
- Use Redis for job queue
- Batch notifications
- Implement rate limiting

---

## ✅ Success Checklist

After implementation, verify:

- [ ] CSV upload works
- [ ] Absent students identified correctly
- [ ] Notifications triggered automatically
- [ ] SMS sent successfully
- [ ] Voice calls made successfully
- [ ] Notifications logged in database
- [ ] Duplicate prevention works
- [ ] Error handling works
- [ ] Retry mechanism works
- [ ] Statistics endpoint works
- [ ] Backend logs are clear
- [ ] All tests pass

---

## 🎉 Summary

The attendance notification system is now fully functional with:

✅ Automatic notification triggering  
✅ Smart status parsing  
✅ Duplicate prevention  
✅ Comprehensive error handling  
✅ Multi-language support  
✅ Detailed logging  
✅ Retry mechanism  
✅ Statistics tracking  

**Ready for production use!** 🚀
