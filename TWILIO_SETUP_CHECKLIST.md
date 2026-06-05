# Twilio Setup Checklist

Use this checklist to set up and test Twilio integration step by step.

---

## Phase 1: Twilio Account Setup

### Step 1: Create Twilio Account
- [ ] Go to https://www.twilio.com/
- [ ] Click "Sign up" or "Try Twilio Free"
- [ ] Complete registration
- [ ] Verify your email address
- [ ] Verify your phone number

### Step 2: Get Credentials
- [ ] Log in to Twilio Console: https://console.twilio.com/
- [ ] Find "Account SID" on dashboard (starts with "AC")
- [ ] Find "Auth Token" on dashboard (click to reveal)
- [ ] Copy both values to a safe place

### Step 3: Get Phone Number
- [ ] Go to Phone Numbers → Manage → Buy a number
- [ ] Select your country (e.g., India +91, US +1)
- [ ] Filter by capabilities: Check "SMS" and "Voice"
- [ ] Choose a number
- [ ] Click "Buy" (uses trial credit, no charge)
- [ ] Copy the phone number (format: +1234567890)

### Step 4: Verify Test Numbers (Trial Accounts Only)
- [ ] Go to Phone Numbers → Manage → Verified Caller IDs
- [ ] Click "Add a new number"
- [ ] Enter YOUR phone number in E.164 format (+919876543210)
- [ ] Click "Verify"
- [ ] Enter the SMS code you receive
- [ ] Confirm verification successful

---

## Phase 2: Backend Configuration

### Step 5: Update .env File
- [ ] Open `backend/.env` in your editor
- [ ] Add your Twilio credentials:
  ```env
  TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  TWILIO_AUTH_TOKEN="your_auth_token_here"
  TWILIO_PHONE_NUMBER="+1234567890"
  ```
- [ ] Ensure no extra spaces
- [ ] Ensure phone number has + prefix
- [ ] Save the file

### Step 6: Restart Backend
- [ ] Stop backend server (Ctrl+C)
- [ ] Navigate to backend directory: `cd backend`
- [ ] Start server: `uvicorn server:app --host 0.0.0.0 --port 8001 --reload`
- [ ] Check logs for: `✓ Twilio client initialized successfully`
- [ ] If you see warning, check credentials and restart

---

## Phase 3: Testing

### Step 7: Test via Swagger UI
- [ ] Open browser: http://localhost:8001/docs
- [ ] Find `POST /api/auth/login` endpoint
- [ ] Click "Try it out"
- [ ] Enter credentials:
  ```json
  {
    "email": "admin@mlrit.ac.in",
    "password": "admin123"
  }
  ```
- [ ] Click "Execute"
- [ ] Copy the `access_token` from response

### Step 8: Authorize
- [ ] Click "Authorize" button (lock icon at top right)
- [ ] Enter: `Bearer YOUR_TOKEN_HERE` (replace with actual token)
- [ ] Click "Authorize"
- [ ] Click "Close"

### Step 9: Check Twilio Status
- [ ] Find `GET /api/test/twilio-status` endpoint
- [ ] Click "Try it out"
- [ ] Click "Execute"
- [ ] Verify response shows:
  ```json
  {
    "configured": true,
    "message": "Twilio is configured and ready"
  }
  ```
- [ ] If not configured, go back to Step 5

### Step 10: Send Test Notifications
- [ ] Find `POST /api/test/twilio` endpoint
- [ ] Click "Try it out"
- [ ] Enter YOUR verified phone number:
  ```json
  {
    "phone_number": "+919876543210"
  }
  ```
- [ ] Click "Execute"
- [ ] Wait for response (may take 5-10 seconds)

### Step 11: Verify Results
- [ ] Check API response shows both success: true
- [ ] Check your phone for SMS (should arrive within 10 seconds)
- [ ] Check your phone for voice call (should arrive within 5 seconds)
- [ ] Check backend logs for success messages
- [ ] If failed, see troubleshooting section below

---

## Phase 4: Real Data Testing

### Step 12: Create Test Parent
- [ ] Go to http://localhost:3000 (frontend)
- [ ] Login with admin credentials
- [ ] Navigate to "Parents" page
- [ ] Click "Add Parent"
- [ ] Enter details:
  - Name: Your name
  - Phone: YOUR verified phone number (+919876543210)
  - Email: Your email (optional)
  - Relationship: Parent
  - Language: English (or your preference)
- [ ] Click "Create Parent"
- [ ] Note the parent ID or name

### Step 13: Create Test Student
- [ ] Navigate to "Students" page
- [ ] Click "Add Student"
- [ ] Enter details:
  - Roll Number: TEST001
  - Name: Test Student
  - Email: test@example.com (optional)
  - Department: Computer Science
  - Year: 1
  - Parent: Select the parent you just created
- [ ] Click "Create Student"

### Step 14: Upload Attendance
- [ ] Navigate to "Attendance" page
- [ ] Create a CSV file with this content:
  ```csv
  roll_number,date,status,subject
  TEST001,2026-03-31,absent,Mathematics
  ```
- [ ] Save as `test_attendance.csv`
- [ ] Drag and drop the file or click to upload
- [ ] Click "Upload & Process"
- [ ] Wait for success message

### Step 15: Verify Notifications
- [ ] Check your phone for SMS about absence
- [ ] Check your phone for voice call about absence
- [ ] Navigate to "Notifications" page in app
- [ ] Verify 2 notifications (SMS and Voice) are logged
- [ ] Check status is "SENT"
- [ ] If failed, check error message

---

## Phase 5: Monitoring

### Step 16: Check Twilio Console
- [ ] Go to https://console.twilio.com/
- [ ] Navigate to Monitor → Logs → Messages
- [ ] Verify your test SMS appears
- [ ] Check status (should be "delivered")
- [ ] Navigate to Monitor → Logs → Calls
- [ ] Verify your test call appears
- [ ] Check status and duration

### Step 17: Check Costs
- [ ] Go to Billing → Usage in Twilio Console
- [ ] Check SMS count and cost
- [ ] Check voice minutes and cost
- [ ] Verify trial credit remaining
- [ ] Set up billing alerts if needed

---

## Troubleshooting Checklist

### If "Twilio not configured" error:
- [ ] Check all 3 credentials are in .env
- [ ] Check no extra spaces in credentials
- [ ] Check Account SID starts with "AC"
- [ ] Restart backend server
- [ ] Check logs for initialization message

### If "Invalid phone number" error:
- [ ] Check phone number format: +[country][number]
- [ ] No spaces: ❌ +91 9876543210
- [ ] No dashes: ❌ +91-9876-543210
- [ ] Correct: ✅ +919876543210

### If "Number is unverified" error (Trial):
- [ ] Go to Twilio Console
- [ ] Phone Numbers → Verified Caller IDs
- [ ] Add and verify the phone number
- [ ] Try again

### If "Authenticate" error:
- [ ] Check Account SID is correct
- [ ] Check Auth Token is correct
- [ ] Try regenerating Auth Token in Twilio
- [ ] Update .env and restart

### If no SMS/call received:
- [ ] Check Twilio Console logs
- [ ] Verify phone number is correct
- [ ] Check phone has signal
- [ ] Check phone can receive SMS/calls
- [ ] Try a different phone number

---

## Success Criteria

You've successfully set up Twilio when:
- ✅ Backend logs show "Twilio client initialized successfully"
- ✅ `/api/test/twilio-status` returns configured: true
- ✅ Test SMS received on your phone
- ✅ Test voice call received on your phone
- ✅ Real attendance notifications work
- ✅ Notifications logged in database
- ✅ Twilio Console shows messages and calls

---

## Next Steps After Setup

### For Development:
- [ ] Test with multiple students
- [ ] Test different languages
- [ ] Test retry mechanism
- [ ] Monitor logs for errors

### For Production:
- [ ] Upgrade Twilio account (remove trial restrictions)
- [ ] Add payment method
- [ ] Set up billing alerts
- [ ] Implement rate limiting
- [ ] Set up monitoring/alerting
- [ ] Add retry queue (Celery)
- [ ] Review security settings

---

## Quick Reference

### Important URLs:
- Twilio Console: https://console.twilio.com/
- Swagger UI: http://localhost:8001/docs
- Frontend: http://localhost:3000

### Test Credentials:
- Email: admin@mlrit.ac.in
- Password: admin123

### Test Endpoints:
- Status: GET /api/test/twilio-status
- Test: POST /api/test/twilio

### Phone Format:
- India: +919876543210
- US: +14155551234
- UK: +447700900123

---

## Documentation Reference

For more details, see:
- **Quick Test:** `TWILIO_QUICK_TEST.md`
- **Comprehensive Guide:** `TWILIO_TESTING_GUIDE.md`
- **Technical Changes:** `TWILIO_INTEGRATION_CHANGES.md`
- **Summary:** `TWILIO_AUDIT_SUMMARY.md`

---

**Checklist Complete!** ✅

Once all items are checked, your Twilio integration is fully set up and tested.
