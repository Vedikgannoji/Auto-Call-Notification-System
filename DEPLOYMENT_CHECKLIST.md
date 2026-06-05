# Production Deployment Checklist

**System:** MLR Institute Auto-Call Notification System  
**Version:** 1.0.0  
**Date:** March 31, 2026

---

## 🎯 Pre-Deployment Checklist

### 1. Environment Setup

#### Backend Environment
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] MongoDB accessible (local or Atlas)
- [ ] Twilio account created and verified
- [ ] Environment variables configured

#### Frontend Environment
- [ ] Node.js 18+ installed
- [ ] Yarn installed globally
- [ ] All dependencies installed (`yarn install`)
- [ ] Build tested (`yarn build`)
- [ ] Environment variables configured

---

## 🔐 Security Configuration

### Backend Security

#### 1. Change Default Credentials
```bash
# Update in backend/.env
JWT_SECRET="your-production-secret-key-min-32-chars"
```

#### 2. Update Admin Password
```bash
cd backend
python seed_admin.py
# Then login and change password via UI
```

#### 3. Configure CORS
```env
# backend/.env
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

#### 4. Secure MongoDB
- [ ] Enable authentication
- [ ] Create dedicated database user
- [ ] Use strong password
- [ ] Restrict IP access
- [ ] Enable SSL/TLS

#### 5. Twilio Security
- [ ] Store credentials in environment variables
- [ ] Never commit credentials to git
- [ ] Use production Twilio account (not trial)
- [ ] Enable webhook authentication
- [ ] Set up IP whitelisting

### Frontend Security
- [ ] Remove console.log statements
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Configure CSP headers
- [ ] Remove development tools

---

## 📝 Configuration Files

### Backend `.env` (Production)
```env
# Database
MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net"
DB_NAME="auto_call_notification_prod"

# Security
JWT_SECRET="your-production-secret-key-min-32-chars-change-this"
CORS_ORIGINS="https://yourdomain.com"

# Twilio
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_production_auth_token"
TWILIO_PHONE_NUMBER="+1234567890"
```

### Frontend `.env` (Production)
```env
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

---

## 🗄️ Database Setup

### MongoDB Production Setup

#### Option 1: MongoDB Atlas (Recommended)
1. [ ] Create MongoDB Atlas account
2. [ ] Create production cluster
3. [ ] Configure network access (whitelist IPs)
4. [ ] Create database user
5. [ ] Get connection string
6. [ ] Update backend/.env

#### Option 2: Self-Hosted MongoDB
1. [ ] Install MongoDB on server
2. [ ] Enable authentication
3. [ ] Create admin user
4. [ ] Create application user
5. [ ] Configure firewall rules
6. [ ] Enable SSL/TLS
7. [ ] Set up automated backups

### Database Indexes (Performance)
```javascript
// Connect to MongoDB
use auto_call_notification_prod

// Create indexes
db.students.createIndex({ "roll_number": 1 }, { unique: true })
db.students.createIndex({ "parent_id": 1 })
db.attendance.createIndex({ "date": 1, "student_id": 1 })
db.attendance.createIndex({ "status": 1 })
db.notifications.createIndex({ "created_at": -1 })
db.notifications.createIndex({ "status": 1 })
db.notifications.createIndex({ "student_id": 1 })
```

### Initial Data Setup
```bash
# Create admin user
cd backend
python seed_admin.py

# Verify admin created
# Login via UI and change password
```

---

## 🚀 Deployment Steps

### Backend Deployment

#### Option 1: Linux Server (Ubuntu/Debian)

1. **Install System Dependencies**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx supervisor
```

2. **Setup Application**
```bash
# Create app directory
sudo mkdir -p /var/www/mlr-autocall
sudo chown $USER:$USER /var/www/mlr-autocall

# Copy files
cd /var/www/mlr-autocall
git clone <your-repo-url> .

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

3. **Configure Supervisor**
```bash
sudo nano /etc/supervisor/conf.d/mlr-backend.conf
```

```ini
[program:mlr-backend]
directory=/var/www/mlr-autocall/backend
command=/var/www/mlr-autocall/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/mlr-backend.err.log
stdout_logfile=/var/log/mlr-backend.out.log
environment=PATH="/var/www/mlr-autocall/venv/bin"
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mlr-backend
```

4. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/mlr-autocall
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/mlr-autocall /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

5. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

#### Option 2: Docker Deployment

1. **Create Dockerfile (Backend)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=${MONGO_URL}
      - DB_NAME=${DB_NAME}
      - JWT_SECRET=${JWT_SECRET}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
    restart: always

  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=your_password
    restart: always

volumes:
  mongodb_data:
```

3. **Deploy**
```bash
docker-compose up -d
```

### Frontend Deployment

#### Option 1: Static Hosting (Netlify/Vercel)

1. **Build Production Bundle**
```bash
cd frontend
yarn build
```

2. **Deploy to Netlify**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=build
```

3. **Configure Environment Variables**
- Go to Netlify dashboard
- Site settings → Environment variables
- Add: `REACT_APP_BACKEND_URL=https://api.yourdomain.com`

#### Option 2: Nginx Static Hosting

1. **Build Frontend**
```bash
cd frontend
yarn build
```

2. **Copy to Server**
```bash
sudo cp -r build/* /var/www/html/mlr-autocall/
```

3. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/html/mlr-autocall;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Setup SSL**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🧪 Post-Deployment Testing

### 1. Backend Health Check
```bash
# Test API endpoint
curl https://api.yourdomain.com/api/auth/me

# Should return 401 (unauthorized) - this is correct
```

### 2. Login Test
1. [ ] Open https://yourdomain.com
2. [ ] Login with admin credentials
3. [ ] Verify dashboard loads
4. [ ] Check all menu items work

### 3. Functionality Tests
- [ ] Create parent
- [ ] Create student
- [ ] Upload attendance CSV
- [ ] Verify notifications sent
- [ ] Check notification status
- [ ] Generate report
- [ ] Update settings

### 4. Twilio Integration Test
```bash
# Use test endpoint
curl -X POST https://api.yourdomain.com/api/test/twilio \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

### 5. Performance Test
- [ ] Upload CSV with 100 students
- [ ] Monitor processing time
- [ ] Check memory usage
- [ ] Verify all notifications sent

---

## 📊 Monitoring Setup

### 1. Application Logs

#### Backend Logs
```bash
# Supervisor logs
tail -f /var/log/mlr-backend.out.log
tail -f /var/log/mlr-backend.err.log

# Or with Docker
docker logs -f mlr-backend
```

#### Frontend Logs
```bash
# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

### 2. Database Monitoring
```javascript
// MongoDB stats
db.stats()

// Collection sizes
db.students.count()
db.parents.count()
db.attendance.count()
db.notifications.count()

// Recent notifications
db.notifications.find().sort({created_at: -1}).limit(10)
```

### 3. Twilio Monitoring
- [ ] Set up usage alerts in Twilio console
- [ ] Monitor daily SMS/call usage
- [ ] Check error rates
- [ ] Set up low balance alerts

### 4. Uptime Monitoring
- [ ] Set up UptimeRobot or similar
- [ ] Monitor API endpoint
- [ ] Monitor frontend URL
- [ ] Set up email alerts

---

## 🔄 Backup Strategy

### Database Backups

#### Automated Daily Backup
```bash
#!/bin/bash
# /usr/local/bin/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb"
DB_NAME="auto_call_notification_prod"

mkdir -p $BACKUP_DIR

mongodump --uri="mongodb://username:password@localhost:27017/$DB_NAME" \
  --out="$BACKUP_DIR/backup_$DATE"

# Keep only last 7 days
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +
```

#### Setup Cron Job
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-mongodb.sh
```

### Application Backups
```bash
# Backup application files
tar -czf /backups/app_$(date +%Y%m%d).tar.gz /var/www/mlr-autocall

# Backup environment files
cp /var/www/mlr-autocall/backend/.env /backups/env_$(date +%Y%m%d).env
```

---

## 🚨 Disaster Recovery

### Database Restore
```bash
# Restore from backup
mongorestore --uri="mongodb://username:password@localhost:27017" \
  --drop /backups/mongodb/backup_20260331_020000
```

### Application Restore
```bash
# Stop services
sudo supervisorctl stop mlr-backend

# Restore files
tar -xzf /backups/app_20260331.tar.gz -C /

# Restart services
sudo supervisorctl start mlr-backend
```

---

## 📈 Performance Optimization

### Backend Optimization
- [ ] Enable gzip compression in Nginx
- [ ] Set up Redis for caching (future)
- [ ] Optimize database queries
- [ ] Add connection pooling
- [ ] Enable HTTP/2

### Frontend Optimization
- [ ] Enable gzip compression
- [ ] Set up CDN for static assets
- [ ] Optimize images
- [ ] Enable browser caching
- [ ] Minify CSS/JS (done in build)

### Database Optimization
- [ ] Create indexes (see above)
- [ ] Enable query profiling
- [ ] Monitor slow queries
- [ ] Set up read replicas (if needed)

---

## 🔧 Maintenance Tasks

### Daily
- [ ] Check application logs for errors
- [ ] Monitor Twilio usage
- [ ] Check failed notifications
- [ ] Verify backups completed

### Weekly
- [ ] Review system performance
- [ ] Check disk space
- [ ] Update dependencies (if needed)
- [ ] Review security logs

### Monthly
- [ ] Update system packages
- [ ] Review and archive old data
- [ ] Test disaster recovery
- [ ] Review Twilio costs
- [ ] Update documentation

---

## 📞 Support & Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check logs
sudo supervisorctl tail -f mlr-backend stderr

# Check if port is in use
sudo netstat -tulpn | grep 8001

# Restart service
sudo supervisorctl restart mlr-backend
```

#### Database Connection Failed
```bash
# Check MongoDB status
sudo systemctl status mongodb

# Test connection
mongo --eval "db.version()"

# Check credentials in .env
```

#### Notifications Not Sending
```bash
# Check Twilio credentials
curl -X GET https://api.yourdomain.com/api/test/twilio-status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check backend logs for Twilio errors
tail -f /var/log/mlr-backend.err.log | grep -i twilio
```

---

## ✅ Final Checklist

### Pre-Launch
- [ ] All security configurations applied
- [ ] Database backups configured
- [ ] SSL certificates installed
- [ ] Monitoring set up
- [ ] Twilio production account configured
- [ ] Admin password changed
- [ ] All tests passed
- [ ] Documentation updated

### Launch Day
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Verify all services running
- [ ] Test complete workflow
- [ ] Monitor logs for errors
- [ ] Send test notifications
- [ ] Train admin users

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Check error rates
- [ ] Verify backups working
- [ ] Collect user feedback
- [ ] Document any issues
- [ ] Plan improvements

---

## 📚 Documentation

### For Admins
- [ ] `DAILY_OPERATIONS_GUIDE.md` - Daily usage guide
- [ ] `QUICKSTART.md` - Getting started
- [ ] `FINAL_ATTENDANCE_SYSTEM.md` - Complete system guide

### For Developers
- [ ] `README.md` - System overview
- [ ] `ARCHITECTURE.md` - Technical architecture
- [ ] `TECHNICAL_ANALYSIS_REPORT.md` - Code analysis

### For Support
- [ ] `SYSTEM_STATUS.md` - Current system status
- [ ] `TWILIO_TESTING_GUIDE.md` - Twilio troubleshooting
- [ ] This file - Deployment guide

---

## 🎉 Deployment Complete!

Once all items are checked:
1. System is live and operational
2. Monitoring is active
3. Backups are configured
4. Users are trained
5. Support is ready

**Congratulations on deploying the MLR Institute Auto-Call Notification System!**

---

**Last Updated:** March 31, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
