# Auto-Call Notification System - System Architecture

## 1. System Overview

### Purpose
Automated attendance monitoring and parent notification system for MLR Institute of Technology.

### Key Components
1. **Admin Web Dashboard** - React-based frontend
2. **REST API Server** - FastAPI backend
3. **Database** - MongoDB
4. **Notification Service** - Twilio integration
5. **Background Job Processor** - FastAPI BackgroundTasks

## 2. Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                      Client Layer                          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         React Admin Dashboard (Port 3000)           │  │
│  │  - Students Management                              │  │
│  │  - Parents Management                               │  │
│  │  - Attendance Upload                                │  │
│  │  - Notifications Log                                │  │
│  │  - Reports & Analytics                              │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────────────────────┘
                     │ HTTPS/REST
                     │
┌────────────────────▼───────────────────────────────────────┐
│                   Application Layer                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │      FastAPI Backend Server (Port 8001)             │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │         Authentication Module               │  │  │
│  │  │  - JWT Token Generation                     │  │  │
│  │  │  - Password Hashing (bcrypt)               │  │  │
│  │  │  - Admin User Management                    │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │         Business Logic Layer                │  │  │
│  │  │  - Student CRUD Operations                  │  │  │
│  │  │  - Parent CRUD Operations                   │  │  │
│  │  │  - Attendance Processing                    │  │  │
│  │  │  - Notification Management                  │  │  │
│  │  │  - Report Generation                        │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │      Background Job Processor               │  │  │
│  │  │  - Attendance Upload Handler                │  │  │
│  │  │  - Absentee Detection                       │  │  │
│  │  │  - Notification Dispatcher                  │  │  │
│  │  │  - Retry Mechanism                          │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────┬───────────────┬───────────────────────┘
                     │               │
                     │               │
        ┌────────────▼──────┐  ┌────▼─────────────────────┐
        │   Data Layer      │  │  External Services       │
        │                   │  │                          │
        │  ┌─────────────┐ │  │  ┌────────────────────┐  │
        │  │  MongoDB     │ │  │  │   Twilio API       │  │
        │  │              │ │  │  │  - SMS Service     │  │
        │  │ Collections: │ │  │  │  - Voice Calls     │  │
        │  │ - students   │ │  │  │  - TwiML Engine   │  │
        │  │ - parents    │ │  │  └────────────────────┘  │
        │  │ - attendance │ │  │                          │
        │  │ - notificati…│ │  │                          │
        │  │ - admin_users│ │  │                          │
        │  │ - templates  │ │  │                          │
        │  └─────────────┘ │  │                          │
        └──────────────────┘  └──────────────────────────┘
```

## 3. Data Flow

### 3.1 Attendance Upload Flow

```
[Admin] → [Upload CSV] → [FastAPI Endpoint]
                              ↓
                    [Validate CSV Format]
                              ↓
                    [Parse Student Records]
                              ↓
                    [Match Roll Numbers]
                              ↓
                    [Save to attendance collection]
                              ↓
                [Trigger Background Job]
                              ↓
                    [Detect Absentees]
                              ↓
                [Fetch Parent Details]
                              ↓
         ┌──────────────────┴──────────────────┐
         ↓                                      ↓
    [Send SMS]                          [Make Voice Call]
         ↓                                      ↓
    [Log Result]                          [Log Result]
         ↓                                      ↓
         └──────────────────┬──────────────────┘
                            ↓
                [Update Notification Status]
```

### 3.2 Authentication Flow

```
[Admin] → [Login Form] → [POST /api/auth/login]
                              ↓
                    [Validate Credentials]
                              ↓
                    [Generate JWT Token]
                              ↓
                    [Return Token + User]
                              ↓
          [Store in localStorage]
                              ↓
      [Include in Authorization Header]
                              ↓
        [Access Protected Routes]
```

### 3.3 Notification Retry Flow

```
[Failed Notification] → [Admin Clicks Retry]
                              ↓
                    [Check Retry Count < 3]
                              ↓
                    [Increment Retry Count]
                              ↓
                    [Attempt Resend]
                              ↓
            ┌──────────────┴──────────────┐
            ↓                              ↓
        [Success]                     [Failure]
            ↓                              ↓
    [Mark as Sent]              [Log Error Message]
    [Update sent_at]            [Status: Failed]
```

## 4. Database Design

### 4.1 Entity-Relationship Diagram

```
┌─────────────────┐
│  admin_users    │
├─────────────────┤
│ id (PK)         │
│ email           │
│ full_name       │
│ hashed_password │
│ role            │
│ created_at      │
└─────────────────┘

┌─────────────────┐        ┌─────────────────┐
│    parents      │        │    students     │
├─────────────────┤        ├─────────────────┤
│ id (PK)         │◄──────┤ parent_id (FK)  │
│ name            │        │ id (PK)         │
│ phone_number    │        │ roll_number     │
│ email           │        │ name            │
│ relationship    │        │ email           │
│ preferred_lang  │        │ department      │
│ created_at      │        │ year            │
└─────────────────┘        │ created_at      │
                           └─────────────────┘
                                    │
                                    │
                                    ▼
                           ┌─────────────────┐
                           │   attendance    │
                           ├─────────────────┤
                           │ id (PK)         │
                           │ student_id (FK) │
                           │ date            │
                           │ status          │
                           │ subject         │
                           │ created_at      │
                           └─────────────────┘
                                    │
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ notifications   │
                           ├─────────────────┤
                           │ id (PK)         │
                           │ student_id (FK) │
                           │ parent_id (FK)  │
                           │ type            │
                           │ status          │
                           │ message         │
                           │ phone_number    │
                           │ retry_count     │
                           │ error_message   │
                           │ sent_at         │
                           │ created_at      │
                           └─────────────────┘

┌──────────────────┐
│ voice_templates  │
├──────────────────┤
│ id (PK)          │
│ language         │
│ message          │
│ created_at       │
└──────────────────┘
```

### 4.2 Indexes

Recommended indexes for performance:

```javascript
// students collection
db.students.createIndex({ "roll_number": 1 }, { unique: true })
db.students.createIndex({ "parent_id": 1 })

// attendance collection
db.attendance.createIndex({ "student_id": 1 })
db.attendance.createIndex({ "date": 1 })
db.attendance.createIndex({ "date": 1, "status": 1 })

// notifications collection
db.notifications.createIndex({ "status": 1 })
db.notifications.createIndex({ "created_at": -1 })
db.notifications.createIndex({ "student_id": 1, "created_at": -1 })

// admin_users collection
db.admin_users.createIndex({ "email": 1 }, { unique: true })
```

## 5. API Architecture

### 5.1 RESTful Principles

- **Resource-based URLs**: `/api/students`, `/api/parents`
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: 200, 201, 400, 401, 404, 500
- **JSON Responses**: Consistent format

### 5.2 Authentication

- **Type**: JWT (JSON Web Tokens)
- **Header**: `Authorization: Bearer <token>`
- **Expiry**: 24 hours
- **Protected Routes**: All except login/register

### 5.3 Error Handling

```json
{
  "detail": "Error message"
}
```

## 6. Security Architecture

### 6.1 Security Layers

1. **Transport Security**: HTTPS (TLS 1.3)
2. **Authentication**: JWT tokens
3. **Password Security**: Bcrypt hashing
4. **API Security**: Token validation middleware
5. **Input Validation**: Pydantic models
6. **CORS**: Configured origins

### 6.2 Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| SQL Injection | MongoDB (NoSQL), input validation |
| XSS | React auto-escaping |
| CSRF | JWT in headers (not cookies) |
| Brute Force | Rate limiting (implement) |
| Data Breach | Encrypted passwords, HTTPS |

## 7. Scalability Design

### 7.1 Current Capacity
- Handles 1000+ students
- Concurrent notifications via background jobs
- Async database operations

### 7.2 Scaling Strategies

**Horizontal Scaling:**
- Deploy multiple backend instances
- Load balancer (Nginx/HAProxy)
- Session-less JWT authentication

**Database Scaling:**
- MongoDB replication
- Sharding for large datasets
- Read replicas

**Queue System (Future):**
- Replace BackgroundTasks with Celery/RabbitMQ
- Better job distribution
- Retry mechanisms

## 8. Monitoring & Logging

### 8.1 Application Logging

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 8.2 Metrics to Monitor

- API response times
- Database query performance
- Notification success/failure rates
- Active user sessions
- Background job queue length

## 9. Deployment Architecture

### 9.1 Production Stack

```
[Internet] → [Nginx Reverse Proxy]
                    ↓
        ┌───────────┴────────────┐
        ↓                        ↓
  [FastAPI:8001]          [React Build:3000]
        ↓
  [MongoDB:27017]
```

### 9.2 Process Management

- **Supervisor**: Process monitoring and auto-restart
- **systemd**: Service management
- **Nginx**: Reverse proxy and SSL termination

## 10. Backup & Recovery

### 10.1 Database Backup

```bash
# Daily backup
mongodump --db auto_call_notification_db --out /backup/$(date +%Y%m%d)

# Restore
mongorestore --db auto_call_notification_db /backup/20260115
```

### 10.2 Recovery Plan

1. Database corruption → Restore from latest backup
2. Server failure → Deploy on new server
3. Data loss → Point-in-time recovery from backups

## 11. Performance Optimization

### 11.1 Backend Optimizations

- Async/await for I/O operations
- Database connection pooling
- Pagination for large datasets
- Caching frequent queries (implement Redis)

### 11.2 Frontend Optimizations

- Code splitting
- Lazy loading routes
- Memoization of components
- Optimized bundle size

## 12. Testing Strategy

### 12.1 Backend Testing

```python
# Unit tests
pytest tests/test_api.py

# Integration tests
pytest tests/test_notification_flow.py
```

### 12.2 Frontend Testing

- Component testing
- End-to-end testing (Playwright)
- User flow testing

## 13. Future Architecture Enhancements

1. **Microservices**: Split into notification service, attendance service
2. **Message Queue**: RabbitMQ/Kafka for reliable job processing
3. **Caching Layer**: Redis for session management
4. **CDN**: Static asset delivery
5. **Container Orchestration**: Docker + Kubernetes
6. **API Gateway**: Kong/AWS API Gateway
7. **Real-time Updates**: WebSocket for live dashboard
