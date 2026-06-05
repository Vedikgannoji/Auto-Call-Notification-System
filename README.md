# Auto-Call Notification System

## Overview

A production-ready web server system for automated attendance monitoring and parent notification through SMS and voice calls. Built specifically for MLR Institute of Technology.

## Features

### Core Functionality
- **Student Management**: Complete CRUD operations for student records
- **Parent Management**: Manage parent contact details with multi-language support
- **Attendance Tracking**: CSV upload and manual entry with automatic absentee detection
- **Automated Notifications**: 
  - SMS alerts via Twilio
  - Voice calls with multi-language support
  - Background job processing
  - Retry mechanism for failed notifications
- **Dashboard Analytics**: Real-time statistics and attendance overview
- **Reports**: Daily attendance summary with percentage calculations
- **Settings**: Customizable voice message templates for different languages

### Technical Features
- JWT-based authentication
- RESTful API architecture
- Scalable to handle 1000+ students
- Real-time notification status tracking
- Comprehensive logging
- Responsive admin dashboard

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: JWT with bcrypt password hashing
- **Notifications**: Twilio API (SMS & Voice)
- **Background Jobs**: FastAPI BackgroundTasks
- **Data Processing**: Pandas (CSV handling)

### Frontend
- **Framework**: React 19
- **UI Components**: Shadcn UI + Radix UI
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **State Management**: React Context API
- **Charts**: Recharts
- **File Upload**: react-dropzone

## Architecture

```
┌─────────────────┐
│   Admin Web     │
│   Dashboard     │
└────────┬────────┘
         │
         │ HTTPS/REST API
         │
┌────────▼────────┐       ┌──────────────┐
│   FastAPI       │       │   Twilio     │
│   Backend       │──────▶│   API        │
└────────┬────────┘       └──────────────┘
         │
         │
┌────────▼────────┐
│   MongoDB       │
│   Database      │
└─────────────────┘
```

## Database Schema

### Collections

1. **admin_users**
   - id, email, full_name, role, hashed_password, created_at

2. **students**
   - id, roll_number, name, email, department, year, parent_id, created_at

3. **parents**
   - id, name, phone_number, email, relationship, preferred_language, created_at

4. **attendance**
   - id, student_id, date, status, subject, created_at

5. **notifications**
   - id, student_id, parent_id, type, status, message, phone_number, retry_count, error_message, sent_at, created_at

6. **voice_templates**
   - id, language, message, created_at

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new admin
- `POST /api/auth/login` - Admin login
- `GET /api/auth/me` - Get current user

### Students
- `POST /api/students` - Create student
- `GET /api/students` - List all students
- `GET /api/students/{id}` - Get student by ID
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student

### Parents
- `POST /api/parents` - Create parent
- `GET /api/parents` - List all parents
- `GET /api/parents/{id}` - Get parent by ID
- `PUT /api/parents/{id}` - Update parent
- `DELETE /api/parents/{id}` - Delete parent

### Attendance
- `POST /api/attendance` - Create attendance record
- `GET /api/attendance` - List attendance records
- `POST /api/attendance/upload-csv` - Upload CSV file
- `POST /api/attendance/trigger-notifications` - Manually trigger notifications

### Notifications
- `GET /api/notifications` - List all notifications
- `POST /api/notifications/{id}/retry` - Retry failed notification

### Voice Templates
- `POST /api/voice-templates` - Create template
- `GET /api/voice-templates` - List templates
- `PUT /api/voice-templates/{id}` - Update template

### Dashboard & Reports
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/reports/daily-summary` - Get daily attendance summary

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Twilio Account (for SMS/Voice)

### Backend Setup

1. Navigate to backend directory:
```bash
cd /app/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="auto_call_notification_db"
JWT_SECRET="your-secret-key-change-in-production"
TWILIO_ACCOUNT_SID="your_twilio_account_sid"
TWILIO_AUTH_TOKEN="your_twilio_auth_token"
TWILIO_PHONE_NUMBER="your_twilio_phone_number"
```

4. Create initial admin user:
```bash
python seed_admin.py
```

5. Start the server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd /app/frontend
```

2. Install dependencies:
```bash
yarn install
```

3. Configure environment variables in `.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

4. Start the development server:
```bash
yarn start
```

## Twilio Configuration

### Getting Twilio Credentials

1. Sign up at [Twilio.com](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the console
3. Purchase a phone number with SMS and Voice capabilities
4. Add credentials to backend `.env` file

### Voice Call Setup

The system uses Twilio's TwiML for voice calls. Messages are dynamically generated based on:
- Parent's preferred language
- Student name and roll number
- Absence date

## CSV Upload Format

### Required Columns
- `roll_number` - Student's roll number
- `date` - Date in YYYY-MM-DD format
- `status` - "present" or "absent"

### Optional Columns
- `subject` - Subject name

### Example CSV
```csv
roll_number,date,status,subject
2021001,2026-01-15,present,Mathematics
2021002,2026-01-15,absent,Mathematics
2021003,2026-01-15,present,Mathematics
```

## Notification Flow

1. Admin uploads attendance CSV or enters manually
2. System detects absent students
3. Background job retrieves parent details
4. SMS sent to parent's phone
5. After 2-second delay, voice call initiated
6. All notifications logged with status
7. Failed notifications can be retried (max 3 attempts)

## Multi-Language Support

Supported languages for voice messages:
- English
- Hindi
- Telugu
- Tamil

Templates use placeholders:
- `{parent_name}` - Parent's name
- `{student_name}` - Student's name
- `{date}` - Absence date

## Default Credentials

**Admin Login:**
- Email: admin@mlrit.ac.in
- Password: admin123

⚠️ **Important**: Change default credentials in production!

## Security Features

- Bcrypt password hashing
- JWT token authentication
- Protected API routes
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention (MongoDB)

## Production Deployment

### Linux Server Setup

1. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm mongodb nginx
```

2. **Configure Nginx** as reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Setup systemd services** for auto-restart

4. **Enable SSL** with Let's Encrypt:
```bash
sudo certbot --nginx -d your-domain.com
```

## Performance Optimization

- **Database Indexing**: Create indexes on frequently queried fields:
  - students: roll_number, parent_id
  - attendance: date, student_id
  - notifications: status, created_at

- **Background Processing**: Notifications sent asynchronously
- **Connection Pooling**: MongoDB connection reuse
- **Pagination**: Implemented for large datasets (if needed)

## Troubleshooting

### Backend Issues

**Server won't start:**
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Verify MongoDB is running
sudo systemctl status mongodb
```

**Twilio errors:**
- Verify credentials are correct
- Check phone number format (E.164: +919876543210)
- Ensure sufficient Twilio credit

### Frontend Issues

**API connection failed:**
- Verify REACT_APP_BACKEND_URL in .env
- Check backend server is running
- Inspect browser console for CORS errors

## Monitoring & Logs

### Backend Logs
```bash
# Application logs
tail -f /var/log/supervisor/backend.out.log

# Error logs
tail -f /var/log/supervisor/backend.err.log
```

### Database Monitoring
```bash
# Connect to MongoDB
mongo

# Use database
use auto_call_notification_db

# Check collections
show collections

# View recent notifications
db.notifications.find().sort({created_at: -1}).limit(10)
```

## Future Enhancements

- Email notifications
- WhatsApp integration
- Mobile app for parents
- Real-time dashboard updates (WebSocket)
- Advanced analytics and reports
- Bulk SMS/Voice campaigns
- Scheduled notifications
- Integration with student portal

## Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation
3. Check backend/frontend logs
4. Contact system administrator

## License

Proprietary - MLR Institute of Technology

## Credits

Developed for MLR Institute of Technology
Auto-Call Notification System v1.0
