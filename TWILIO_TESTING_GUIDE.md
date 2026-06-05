# Twilio Integration Testing Guide

## Overview
This guide explains how to test the improved Twilio SMS and Voice Call integration in the MLR Institute Auto-Call Notification System.

---

## What Was Fixed

### 1. Twilio Client Initialization
✅ **Before:** Basic initialization without validation  
✅ **After:** 
- Validates all required credentials (Account SID, Auth Token, Phone Number)
- Logs initialization status
- Provides clear error messages for missing credentials
- Strips whitespace from credentials

### 2. SMS Function (`send_sms`)
✅ **Improvements:**
- Comprehensive error handling
- Structured logging (success/failure)
- Clear return format: `(success: bool, result: str)`
- Detailed error messages
- Logs message SID and status

### 3. Voice Call Function (`make_voice_call`)
✅ **Improvements:**
- Multi-language support (English, Hindi, Tamil, Telugu)
- XML character escaping for safety
- Language code mapping
- Better error handling
- Logs call SID and status

### 4. New Test Endpoints
✅ **Added:**
- `POST /api/test/twilio` - Send test SMS and voice call
- `GET /api/test/twilio-status` - Check Twilio configuration status

---

## Prerequisites

### 1. Twilio Account Setup

**Step 1:** Sign up for Twilio
- Go to https://www.twilio.com/
- Create a free trial account (gets $15 credit)
- Verify your email and phone number

**Step 2:** Get Credentials
1. Log in to Twilio Console: https://console.twilio.com/
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Copy both values

**Step 3:** Get Phone Number
1. Go to Phone Numbers → Manage → Buy a number
2. Choose a number with **SMS** and **Voice** capabilities
3. For India: Select country code +91
4. Complete purchase (uses trial credit)

**Step 4:** Verify Test Numbers (Trial Accounts Only)
1. Go to Phone Numbers → Manage → Verified Caller IDs
2. Click "Add a new number"
3. Enter your phone number in E.164 format: `+919876543210`
4. Verify via SMS code

---

## Configuration

### Update Backend .env File

Open `backend/.env` and add your Twilio credentials:

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="auto_call_notification_db"
CORS_ORIGINS="*"
JWT_SECRET="your-secret-key-change-in-production-12345"

# Twilio Configuration
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token_here"
TWILIO_PHONE_NUMBER="+1234567890"
```

**Important Notes:**
- Account SID starts with "AC"
- Phone number must be in E.164 format: `+[country_code][number]`
- No spaces in credentials
- For India: `+919876543210`
- For US: `+14155551234`

### Restart Backend Server

After updating .env, restart the backend:

```bash
# Stop the server (Ctrl+C)
# Then restart
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

You should see in the logs:
```
INFO:root:✓ Twilio client initialized successfully with phone number: +1234567890
```

If credentials are missing:
```
WARNING:root:⚠ Twilio not configured. Missing: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
```

---

## Testing Methods

### Method 1: Using Swagger UI (Easiest)

1. **Open Swagger UI**
   - Navigate to: http://localhost:8001/docs
   - You'll see the FastAPI interactive documentation

2. **Authenticate**
   - Click the "Authorize" button (lock icon)
   - Login first via `/api/auth/login` endpoint:
     - Email: `admin@mlrit.ac.in`
     - Password: `admin123`
   - Copy the `access_token` from response
   - Click "Authorize" and enter: `Bearer YOUR_TOKEN_HERE`
   - Click "Authorize" then "Close"

3. **Check Twilio Status**
   - Find `GET /api/test/twilio-status`
   - Click "Try it out"
   - Click "Execute"
   - Should show:
     ```json
     {
       "configured": true,
       "account_sid": "ACxxxxxxxx...",
       "phone_number": "+1234567890",
       "message": "Twilio is configured and ready"
     }
     ```

4. **Send Test Notifications**
   - Find `POST /api/test/twilio`
   - Click "Try it out"
   - Enter your phone number in E.164 format:
     ```json
     {
       "phone_number": "+919876543210"
     }
     ```
   - Click "Execute"
   - Check response:
     ```json
     {
       "twilio_configured": true,
       "sms_result": {
         "success": true,
         "message_sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
         "error": null
       },
       "voice_result": {
         "success": true,
         "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
         "error": null
       },
       "message": "✓ Both SMS and voice call sent successfully! Check your phone."
     }
     ```

5. **Check Your Phone**
   - You should receive an SMS within seconds
   - You should receive a voice call within 2-5 seconds after SMS

---

### Method 2: Using cURL (Command Line)

**Step 1: Login and Get Token**
```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@mlrit.ac.in\",\"password\":\"admin123\"}"
```

Copy the `access_token` from response.

**Step 2: Check Twilio Status**
```bash
curl -X GET "http://localhost:8001/api/test/twilio-status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Step 3: Send Test Notifications**
```bash
curl -X POST "http://localhost:8001/api/test/twilio" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\":\"+919876543210\"}"
```

---

### Method 3: Using Postman

1. **Import Collection**
   - Create new request
   - Method: POST
   - URL: `http://localhost:8001/api/auth/login`
   - Body (JSON):
     ```json
     {
       "email": "admin@mlrit.ac.in",
       "password": "admin123"
     }
     ```
   - Send and copy `access_token`

2. **Set Authorization**
   - Create new request
   - Method: POST
   - URL: `http://localhost:8001/api/test/twilio`
   - Headers:
     - Key: `Authorization`
     - Value: `Bearer YOUR_TOKEN_HERE`
   - Body (JSON):
     ```json
     {
       "phone_number": "+919876543210"
     }
     ```
   - Send

---

## Expected Results

### Successful Test

**SMS:**
- Message received within 5-10 seconds
- Content: "Hello! This is a test SMS from MLR Institute Auto-Call System. Sent at [timestamp] UTC."

**Voice Call:**
- Call received within 2-5 seconds after SMS
- Message: "Hello! This is a test call from M L R Institute Auto-Call Notification System. If you can hear this message, your Twilio integration is working correctly."

**API Response:**
```json
{
  "twilio_configured": true,
  "sms_result": {
    "success": true,
    "message_sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "error": null
  },
  "voice_result": {
    "success": true,
    "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "error": null
  },
  "message": "✓ Both SMS and voice call sent successfully! Check your phone."
}
```

**Backend Logs:**
```
INFO:root:Attempting to send SMS to +919876543210
INFO:root:✓ SMS sent successfully to +919876543210. SID: SMxxxx, Status: queued
INFO:root:Attempting to make voice call to +919876543210 in language: en-IN
INFO:root:✓ Voice call initiated successfully to +919876543210. SID: CAxxxx, Status: queued
```

---

## Troubleshooting

### Issue 1: "Twilio not configured"

**Symptoms:**
```json
{
  "twilio_configured": false,
  "message": "Twilio credentials are missing..."
}
```

**Solution:**
1. Check `backend/.env` has all three credentials
2. Ensure no extra spaces in values
3. Restart backend server
4. Check logs for initialization message

---

### Issue 2: "Unable to create record: The 'To' number is not a valid phone number"

**Symptoms:**
```json
{
  "sms_result": {
    "success": false,
    "error": "SMS sending failed: Unable to create record: The 'To' number..."
  }
}
```

**Solution:**
- Phone number must be in E.164 format
- Include country code with +
- Examples:
  - ✅ Correct: `+919876543210` (India)
  - ✅ Correct: `+14155551234` (US)
  - ❌ Wrong: `9876543210`
  - ❌ Wrong: `+91 9876543210` (space)
  - ❌ Wrong: `+91-9876543210` (dash)

---

### Issue 3: "The number is unverified" (Trial Accounts)

**Symptoms:**
```json
{
  "error": "The number +919876543210 is unverified. Trial accounts cannot send messages to unverified numbers"
}
```

**Solution:**
1. Go to Twilio Console
2. Navigate to Phone Numbers → Manage → Verified Caller IDs
3. Click "Add a new number"
4. Enter the phone number you want to test
5. Verify via SMS code
6. Try again

---

### Issue 4: "Authenticate" (Invalid Credentials)

**Symptoms:**
```json
{
  "error": "Authenticate"
}
```

**Solution:**
1. Verify Account SID and Auth Token are correct
2. Check for typos or extra spaces
3. Regenerate Auth Token in Twilio Console if needed
4. Update .env and restart server

---

### Issue 5: SMS Works but Voice Call Fails

**Symptoms:**
- SMS: ✅ Success
- Voice: ❌ Failed

**Possible Causes:**
1. Phone number doesn't support voice calls
2. Twilio phone number doesn't have voice capability
3. Network/carrier blocking calls

**Solution:**
1. Check Twilio phone number capabilities
2. Try a different test number
3. Check Twilio Console → Logs for detailed error

---

### Issue 6: No SMS/Call Received

**Symptoms:**
- API returns success
- But no SMS/call received

**Solution:**
1. Check Twilio Console → Logs → Messages/Calls
2. Verify phone number is correct
3. Check phone signal/network
4. For trial accounts: Ensure number is verified
5. Check Twilio account balance

---

## Testing Real Notification Flow

Once Twilio is working, test the full attendance notification flow:

### Step 1: Create Test Data

1. **Add a Parent**
   - Go to Parents page
   - Add parent with YOUR verified phone number
   - Set preferred language (English/Hindi/Tamil/Telugu)

2. **Add a Student**
   - Go to Students page
   - Add student linked to the parent above

### Step 2: Upload Attendance

1. Create a CSV file with absent student:
   ```csv
   roll_number,date,status,subject
   2021001,2026-03-31,absent,Mathematics
   ```

2. Go to Attendance page
3. Upload the CSV file
4. Check backend logs for notification processing

### Step 3: Verify Notifications

1. Check your phone for SMS and voice call
2. Go to Notifications page in the app
3. Verify both SMS and voice notifications are logged
4. Check status (sent/failed)

---

## Monitoring Twilio Usage

### Check Twilio Console

1. Go to https://console.twilio.com/
2. Navigate to Monitor → Logs → Messages
3. See all SMS sent with status
4. Navigate to Monitor → Logs → Calls
5. See all calls made with duration and status

### Check Costs

1. Go to Billing → Usage
2. See SMS and voice call costs
3. Monitor trial credit balance

**Typical Costs:**
- SMS: ~$0.0075 per message
- Voice: ~$0.013 per minute
- Trial credit: $15 (enough for ~750 SMS or ~1150 minutes)

---

## Production Considerations

### Before Going Live:

1. **Upgrade Twilio Account**
   - Remove trial restrictions
   - Add payment method
   - Set up billing alerts

2. **Phone Number Verification**
   - No longer needed for verified accounts
   - Can send to any number

3. **Rate Limiting**
   - Twilio has rate limits
   - Implement queuing for bulk notifications
   - Consider using Celery for production

4. **Error Handling**
   - Monitor failed notifications
   - Implement retry logic
   - Set up alerts for failures

5. **Compliance**
   - Follow SMS regulations (TCPA, GDPR)
   - Include opt-out mechanism
   - Respect quiet hours

---

## Summary

✅ **What's Working:**
- Twilio client initialization with validation
- SMS sending with proper error handling
- Voice calls with multi-language support
- Test endpoints for easy verification
- Comprehensive logging

✅ **How to Test:**
1. Configure Twilio credentials in .env
2. Restart backend server
3. Use `/api/test/twilio` endpoint
4. Check phone for SMS and call

✅ **Next Steps:**
- Test with real attendance data
- Monitor Twilio logs
- Implement retry mechanism
- Add email notifications
- Set up production monitoring

---

## Need Help?

**Common Issues:**
- Credentials not working → Regenerate in Twilio Console
- Phone format errors → Use E.164 format (+countrycode + number)
- Trial restrictions → Verify phone numbers in Twilio Console
- No messages received → Check Twilio logs for delivery status

**Resources:**
- Twilio Documentation: https://www.twilio.com/docs
- Twilio Console: https://console.twilio.com/
- Support: https://support.twilio.com/

---

**Testing Complete!** 🎉

If you can send test SMS and voice calls successfully, your Twilio integration is working correctly!
