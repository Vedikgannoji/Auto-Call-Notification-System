# Twilio Configuration Guide

To get Twilio working with the Auto-Call Notification System:

## Step 1: Sign Up for Twilio
1. Go to https://www.twilio.com/
2. Create a free trial account
3. Verify your email and phone number

## Step 2: Get Your Credentials

### Account SID and Auth Token
1. Log in to Twilio Console
2. Find your Account SID and Auth Token on the dashboard
3. Copy both values

### Twilio Phone Number
1. Go to Phone Numbers section
2. Buy a phone number (trial gives $15 credit)
3. Choose a number with SMS and Voice capabilities
4. Note: In trial mode, you can only send to verified numbers

## Step 3: Configure Backend

1. Open `/app/backend/.env`
2. Add your credentials:

```env
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token_here"
TWILIO_PHONE_NUMBER="+1234567890"
```

3. Restart backend:
```bash
sudo supervisorctl restart backend
```

## Step 4: Test Notifications

### For Trial Accounts:
- You can only send to verified phone numbers
- Add test numbers in Twilio Console > Phone Numbers > Verified Caller IDs
- Format: +[country code][number] (e.g., +919876543210)

### Testing:
1. Add a parent with verified phone number
2. Upload attendance with absent students
3. Check Notifications page for status

## Troubleshooting

### "Twilio not configured" error
- Verify credentials are in .env
- Restart backend server
- Check credentials are correct (no spaces)

### SMS not received
- Check phone number format (+countrycode)
- Verify number is in E.164 format
- Check Twilio account balance
- For trial: verify recipient number in Twilio

### Voice call failed
- Same checks as SMS
- Ensure phone number has voice capability
- Check Twilio logs in console

## Production Notes

- Remove trial mode by upgrading account
- Set up proper phone number verification
- Monitor usage and billing
- Set up webhooks for delivery status

## Cost Estimation

**Per notification (SMS + Voice):**
- SMS: ~$0.0075 per message
- Voice: ~$0.013 per minute
- Total: ~$0.02 per absent student

**For 100 absent students/day:**
- Daily: $2.00
- Monthly: ~$60
- Annual: ~$720

Prices vary by country and carrier.
