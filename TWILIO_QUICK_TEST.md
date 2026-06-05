# Twilio Quick Test - 5 Minute Guide

## Step 1: Configure (2 minutes)

Edit `backend/.env`:
```env
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token_here"
TWILIO_PHONE_NUMBER="+1234567890"
```

Get credentials from: https://console.twilio.com/

## Step 2: Restart Backend (30 seconds)

```bash
cd backend
# Stop server (Ctrl+C if running)
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Look for this in logs:
```
INFO:root:✓ Twilio client initialized successfully with phone number: +1234567890
```

## Step 3: Test via Swagger UI (2 minutes)

1. Open: http://localhost:8001/docs

2. Login:
   - Find `POST /api/auth/login`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "email": "admin@mlrit.ac.in",
       "password": "admin123"
     }
     ```
   - Click "Execute"
   - Copy the `access_token`

3. Authorize:
   - Click "Authorize" button (lock icon at top)
   - Enter: `Bearer YOUR_TOKEN_HERE`
   - Click "Authorize" then "Close"

4. Check Status:
   - Find `GET /api/test/twilio-status`
   - Click "Try it out"
   - Click "Execute"
   - Should show: `"configured": true`

5. Send Test:
   - Find `POST /api/test/twilio`
   - Click "Try it out"
   - Enter YOUR phone number:
     ```json
     {
       "phone_number": "+919876543210"
     }
     ```
   - Click "Execute"

## Step 4: Check Results (30 seconds)

**Your Phone:**
- SMS should arrive within 5-10 seconds
- Voice call should arrive within 2-5 seconds after SMS

**API Response:**
```json
{
  "twilio_configured": true,
  "sms_result": {
    "success": true,
    "message_sid": "SMxxxx..."
  },
  "voice_result": {
    "success": true,
    "call_sid": "CAxxxx..."
  },
  "message": "✓ Both SMS and voice call sent successfully!"
}
```

**Backend Logs:**
```
INFO:root:Attempting to send SMS to +919876543210
INFO:root:✓ SMS sent successfully to +919876543210. SID: SMxxxx
INFO:root:Attempting to make voice call to +919876543210
INFO:root:✓ Voice call initiated successfully to +919876543210. SID: CAxxxx
```

---

## Troubleshooting

### "Twilio not configured"
- Check .env file has all 3 credentials
- Restart backend server
- Check logs for initialization message

### "Invalid phone number"
- Use E.164 format: `+[country][number]`
- Examples: `+919876543210` (India), `+14155551234` (US)
- No spaces or dashes

### "Number is unverified" (Trial accounts)
- Go to: https://console.twilio.com/
- Phone Numbers → Verified Caller IDs
- Add and verify your test number

### No SMS/Call received
- Check Twilio Console → Logs
- Verify phone number is correct
- Check phone signal
- For trial: Ensure number is verified

---

## Quick cURL Test (Alternative)

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mlrit.ac.in","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 2. Test Twilio
curl -X POST "http://localhost:8001/api/test/twilio" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+919876543210"}'
```

---

## Success Checklist

- [ ] Backend logs show "✓ Twilio client initialized successfully"
- [ ] `/api/test/twilio-status` returns `"configured": true`
- [ ] Test SMS received on phone
- [ ] Test voice call received on phone
- [ ] API response shows both success: true
- [ ] Backend logs show successful SMS and call

---

## Next Steps

Once testing works:
1. Add real parent with your phone number
2. Add student linked to that parent
3. Upload attendance CSV with absent student
4. Verify real notifications work

---

**Need detailed help?** See `TWILIO_TESTING_GUIDE.md`

**See all changes?** See `TWILIO_INTEGRATION_CHANGES.md`
