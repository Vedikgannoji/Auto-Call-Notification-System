# Daily Operations Guide - Quick Reference

**For:** MLR Institute Admin Users  
**System:** Auto-Call Notification System

---

## 🚀 Starting the System

### Every Day Startup

1. **Start MongoDB** (if not running as service)
   ```bash
   net start MongoDB
   ```

2. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   yarn start
   ```

4. **Login**
   - URL: http://localhost:3000
   - Email: admin@mlrit.ac.in
   - Password: admin123

---

## 📋 Daily Attendance Workflow

### Step 1: Prepare CSV File

Create a CSV file with these columns:
```csv
roll_number,date,status,subject
2021001,31-03-2026,present,Mathematics
2021002,31-03-2026,absent,Mathematics
2021003,31-03-2026,0,Physics
```

**Status Options:**
- **Absent:** `absent`, `a`, `0`, `false`
- **Present:** `present`, `p`, `1`, `true`

### Step 2: Upload Attendance

1. Click **Attendance** in sidebar
2. Click **Upload CSV** button
3. Select your CSV file
4. Click **Upload**
5. Wait for success message

### Step 3: Verify Notifications

1. Click **Notifications** in sidebar
2. Check recent notifications
3. Verify status (sent/failed)
4. Retry failed notifications if needed

### Step 4: Check Dashboard

1. Click **Dashboard** in sidebar
2. Review today's statistics:
   - Total students
   - Today's absentees
   - Notifications sent
   - Failed notifications

---

## 👥 Managing Students & Parents

### Add New Parent

1. Click **Parents** → **Add Parent**
2. Fill in details:
   - Name: Parent's full name
   - Phone: **Must be in format +919876543210**
   - Email: Optional
   - Language: english/hindi/tamil/telugu
3. Click **Save**
4. **Note the Parent ID** for linking student

### Add New Student

1. Click **Students** → **Add Student**
2. Fill in details:
   - Roll Number: Unique identifier
   - Name: Student's full name
   - Department: e.g., Computer Science
   - Year: 1, 2, 3, or 4
   - Parent ID: Copy from parent record
3. Click **Save**

### Edit Student/Parent

1. Find the record in list
2. Click **Edit** button
3. Update details
4. Click **Save**

---

## 📊 Generating Reports

### Daily Summary Report

1. Click **Reports** in sidebar
2. Select date from calendar
3. Click **Generate Report**
4. View:
   - Total attendance records
   - Present count
   - Absent count
   - Attendance percentage
   - Notifications sent

---

## 🔔 Notification Management

### Check Notification Status

1. Click **Notifications**
2. View list of all notifications
3. Check status:
   - ✅ **Sent** - Successfully delivered
   - ❌ **Failed** - Delivery failed
   - ⏳ **Pending** - In queue

### Retry Failed Notification

1. Find failed notification
2. Click **Retry** button
3. System will attempt to resend
4. Check status after 10 seconds

### View Notification Statistics

1. Click **Notifications**
2. Click **Statistics** tab
3. Select date range
4. View:
   - Total notifications
   - Success rate
   - SMS vs Voice breakdown

---

## ⚙️ Settings

### Update Voice Message Templates

1. Click **Settings** in sidebar
2. Select language (English/Hindi/Tamil/Telugu)
3. Edit message template
4. Use placeholders:
   - `{student_name}` - Student's name
   - `{parent_name}` - Parent's name
   - `{date}` - Absence date
   - `{subject}` - Subject name
5. Click **Save**

---

## 🚨 Troubleshooting

### Problem: Notifications Not Sending

**Check:**
1. Is Twilio configured? (Settings → Twilio Status)
2. Is phone number in correct format? (+919876543210)
3. Does parent have phone number?
4. Is student linked to parent?

**Solution:**
```bash
# Check backend logs
# Look for error messages
```

### Problem: Student Not Found in CSV Upload

**Check:**
1. Does roll number match exactly?
2. Is student in database?
3. Any extra spaces in CSV?

**Solution:**
1. Go to Students page
2. Search for roll number
3. Verify exact spelling
4. Update CSV to match

### Problem: Parent Not Found

**Check:**
1. Does student have parent_id?
2. Is parent_id correct?

**Solution:**
1. Go to Students page
2. Edit student
3. Verify Parent ID field
4. Copy correct ID from Parents page

### Problem: Login Failed

**Solution:**
```bash
# Re-run seed script
cd backend
python seed_admin.py
```

### Problem: Backend Not Responding

**Solution:**
```bash
# Restart backend
# Press Ctrl+C in backend terminal
# Then run again:
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

---

## 📱 Phone Number Format

### Correct Format (E.164)
```
+919876543210
+918123456789
+911234567890
```

### Incorrect Format
```
9876543210          ❌ Missing country code
+91 9876543210      ❌ Has space
+91-9876543210      ❌ Has dash
919876543210        ❌ Missing + sign
```

---

## 📝 CSV File Tips

### Good CSV Example
```csv
roll_number,date,status,subject
2021001,31-03-2026,absent,Mathematics
2021002,31-03-2026,present,Physics
2021003,31-03-2026,0,Chemistry
```

### Common Mistakes

❌ **Missing columns**
```csv
roll_number,date,status
2021001,31-03-2026,absent
```

❌ **Wrong date format**
```csv
roll_number,date,status,subject
2021001,2026-03-31,absent,Math    # Should be DD-MM-YYYY
```

❌ **Extra spaces**
```csv
roll_number,date,status,subject
2021001 ,31-03-2026, absent ,Math  # Spaces cause issues
```

✅ **Correct Format**
```csv
roll_number,date,status,subject
2021001,31-03-2026,absent,Mathematics
```

---

## 🎯 Quick Checklist

### Before Uploading Attendance
- [ ] CSV has 4 columns: roll_number, date, status, subject
- [ ] Date format is DD-MM-YYYY
- [ ] All students exist in database
- [ ] All students have parent_id
- [ ] All parents have phone numbers
- [ ] Phone numbers are in E.164 format (+91...)

### After Uploading Attendance
- [ ] Check success message
- [ ] Verify absent count is correct
- [ ] Check Notifications page
- [ ] Verify SMS sent
- [ ] Verify voice calls made
- [ ] Check for failed notifications
- [ ] Retry any failures

### End of Day
- [ ] Review Dashboard statistics
- [ ] Generate daily report
- [ ] Check for failed notifications
- [ ] Retry failed notifications
- [ ] Backup database (if needed)

---

## 📞 Support

### If You Need Help

1. **Check Logs**
   - Backend terminal shows detailed logs
   - Look for ❌ error messages
   - Look for ⚠️ warnings

2. **Check Documentation**
   - `FINAL_ATTENDANCE_SYSTEM.md` - Complete guide
   - `TWILIO_TESTING_GUIDE.md` - Twilio issues
   - `QUICKSTART.md` - Setup issues

3. **Common Solutions**
   - Restart backend server
   - Clear browser cache
   - Check MongoDB is running
   - Verify Twilio credentials

---

## 🔐 Security Reminders

### Important
- ⚠️ Change default admin password in production
- ⚠️ Keep Twilio credentials secret
- ⚠️ Don't share JWT tokens
- ⚠️ Log out when done
- ⚠️ Use HTTPS in production

### Default Credentials (CHANGE IN PRODUCTION)
```
Email: admin@mlrit.ac.in
Password: admin123
```

---

## 📊 Understanding the Dashboard

### Statistics Explained

**Total Students**
- Count of all students in database

**Total Parents**
- Count of all parents in database

**Today's Absentees**
- Students marked absent today
- Triggers notifications automatically

**Notifications Sent Today**
- Total SMS + Voice calls sent today
- Includes both successful and failed

**Failed Notifications**
- Notifications that failed to send
- Need manual retry

---

## 🎓 Best Practices

### Daily Operations
1. Upload attendance before 10 AM
2. Check notifications by 11 AM
3. Retry failed notifications immediately
4. Generate daily report at end of day
5. Keep student/parent data updated

### Data Management
1. Add new students at start of semester
2. Update parent phone numbers regularly
3. Archive old attendance records monthly
4. Backup database weekly
5. Clean up test data

### Notification Management
1. Monitor success rate (should be >95%)
2. Retry failed notifications within 1 hour
3. Update phone numbers if consistently failing
4. Check Twilio balance regularly
5. Test with your own number first

---

## 📅 Monthly Tasks

### Start of Month
- [ ] Review previous month's statistics
- [ ] Generate monthly report
- [ ] Check Twilio usage and billing
- [ ] Update voice templates if needed
- [ ] Clean up old test data

### End of Month
- [ ] Backup database
- [ ] Archive old notifications
- [ ] Review failed notifications
- [ ] Update documentation if needed
- [ ] Plan for next month

---

## 🎉 Quick Tips

### Keyboard Shortcuts
- `Ctrl + R` - Refresh page
- `Ctrl + F` - Search in page
- `Esc` - Close dialog/modal

### Time Savers
1. Keep CSV template ready
2. Use copy-paste for parent IDs
3. Bookmark frequently used pages
4. Use browser's back button
5. Keep backend terminal visible

### Pro Tips
1. Test with 1-2 students first
2. Use your own phone for testing
3. Check logs for detailed info
4. Keep Twilio console open
5. Document any issues you find

---

**Remember:** The system automatically sends notifications for absent students. You just need to upload the CSV!

**Questions?** Check `FINAL_ATTENDANCE_SYSTEM.md` for detailed documentation.

---

**Last Updated:** March 31, 2026  
**Version:** 1.0.0
