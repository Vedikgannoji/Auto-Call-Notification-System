#!/usr/bin/env python3
"""
Test script for Attendance Notification System

This script tests the complete flow:
1. Creates test parent
2. Creates test student
3. Uploads attendance CSV
4. Verifies notifications were sent
5. Checks statistics

Usage:
    python test_attendance_notifications.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "admin@mlrit.ac.in"
ADMIN_PASSWORD = "admin123"

# Test data
TEST_PHONE = "+919876543210"  # Replace with your verified phone number
TEST_DATE = datetime.now().strftime("%Y-%m-%d")

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def login():
    """Login and get access token"""
    print_section("Step 1: Login")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful")
        print(f"   Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def create_parent(token):
    """Create test parent"""
    print_section("Step 2: Create Test Parent")
    
    parent_data = {
        "name": "Test Parent",
        "phone_number": TEST_PHONE,
        "email": "testparent@example.com",
        "relationship": "parent",
        "preferred_language": "english"
    }
    
    response = requests.post(
        f"{BASE_URL}/parents",
        headers={"Authorization": f"Bearer {token}"},
        json=parent_data
    )
    
    if response.status_code == 200:
        parent = response.json()
        print(f"✅ Parent created successfully")
        print(f"   ID: {parent['id']}")
        print(f"   Name: {parent['name']}")
        print(f"   Phone: {parent['phone_number']}")
        return parent['id']
    else:
        print(f"❌ Failed to create parent: {response.text}")
        return None

def create_student(token, parent_id):
    """Create test student"""
    print_section("Step 3: Create Test Student")
    
    student_data = {
        "roll_number": f"TEST{int(time.time())}",  # Unique roll number
        "name": "Test Student",
        "email": "teststudent@example.com",
        "department": "Computer Science",
        "year": 1,
        "parent_id": parent_id
    }
    
    response = requests.post(
        f"{BASE_URL}/students",
        headers={"Authorization": f"Bearer {token}"},
        json=student_data
    )
    
    if response.status_code == 200:
        student = response.json()
        print(f"✅ Student created successfully")
        print(f"   ID: {student['id']}")
        print(f"   Name: {student['name']}")
        print(f"   Roll: {student['roll_number']}")
        return student['roll_number']
    else:
        print(f"❌ Failed to create student: {response.text}")
        return None

def upload_attendance_csv(token, roll_number):
    """Upload attendance CSV"""
    print_section("Step 4: Upload Attendance CSV")
    
    # Create CSV content
    csv_content = f"roll_number,date,status,subject\n{roll_number},{TEST_DATE},absent,Mathematics"
    
    # Save to file
    with open("test_attendance.csv", "w") as f:
        f.write(csv_content)
    
    print(f"📄 CSV Content:")
    print(f"   {csv_content}")
    
    # Upload
    with open("test_attendance.csv", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/attendance/upload-csv",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_attendance.csv", f, "text/csv")}
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ CSV uploaded successfully")
        print(f"   Records created: {result['records_created']}")
        print(f"   Records skipped: {result['records_skipped']}")
        print(f"   Date: {result['date']}")
        print(f"   Notifications triggered: {result['notifications_triggered']}")
        return True
    else:
        print(f"❌ Failed to upload CSV: {response.text}")
        return False

def wait_for_notifications():
    """Wait for notifications to be processed"""
    print_section("Step 5: Wait for Notifications")
    
    print("⏳ Waiting 10 seconds for notifications to be processed...")
    for i in range(10, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print("   ✅ Wait complete")

def check_notifications(token):
    """Check notifications"""
    print_section("Step 6: Check Notifications")
    
    response = requests.get(
        f"{BASE_URL}/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        notifications = response.json()
        print(f"✅ Found {len(notifications)} notifications")
        
        for notif in notifications[-2:]:  # Show last 2 (SMS + Voice)
            print(f"\n   Type: {notif['type'].upper()}")
            print(f"   Status: {notif['status']}")
            print(f"   Phone: {notif['phone_number']}")
            print(f"   Message: {notif['message'][:50]}...")
            if notif['error_message']:
                print(f"   Error: {notif['error_message']}")
        
        return len(notifications)
    else:
        print(f"❌ Failed to get notifications: {response.text}")
        return 0

def check_statistics(token):
    """Check notification statistics"""
    print_section("Step 7: Check Statistics")
    
    response = requests.get(
        f"{BASE_URL}/notifications/stats?date={TEST_DATE}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Statistics for {stats['date']}:")
        print(f"   Total notifications: {stats['total_notifications']}")
        print(f"   Sent: {stats['sent']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success rate: {stats['success_rate']}%")
        print(f"\n   SMS: {stats['by_type']['sms']['sent']}/{stats['by_type']['sms']['total']} sent")
        print(f"   Voice: {stats['by_type']['voice']['sent']}/{stats['by_type']['voice']['total']} sent")
        return stats
    else:
        print(f"❌ Failed to get statistics: {response.text}")
        return None

def main():
    """Run the complete test"""
    print("\n" + "🚀 "*20)
    print("  ATTENDANCE NOTIFICATION SYSTEM - TEST SCRIPT")
    print("🚀 "*20)
    
    print(f"\n📋 Test Configuration:")
    print(f"   Backend URL: {BASE_URL}")
    print(f"   Test Phone: {TEST_PHONE}")
    print(f"   Test Date: {TEST_DATE}")
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Test failed: Could not login")
        return
    
    # Step 2: Create parent
    parent_id = create_parent(token)
    if not parent_id:
        print("\n❌ Test failed: Could not create parent")
        return
    
    # Step 3: Create student
    roll_number = create_student(token, parent_id)
    if not roll_number:
        print("\n❌ Test failed: Could not create student")
        return
    
    # Step 4: Upload CSV
    if not upload_attendance_csv(token, roll_number):
        print("\n❌ Test failed: Could not upload CSV")
        return
    
    # Step 5: Wait
    wait_for_notifications()
    
    # Step 6: Check notifications
    notif_count = check_notifications(token)
    
    # Step 7: Check statistics
    stats = check_statistics(token)
    
    # Summary
    print_section("TEST SUMMARY")
    
    if notif_count >= 2 and stats and stats['sent'] >= 2:
        print("✅ TEST PASSED!")
        print("\n   All steps completed successfully:")
        print("   ✓ Parent created")
        print("   ✓ Student created")
        print("   ✓ Attendance uploaded")
        print("   ✓ Notifications sent")
        print("   ✓ Statistics tracked")
        print("\n📱 Check your phone for SMS and voice call!")
    else:
        print("⚠️  TEST PARTIALLY PASSED")
        print("\n   Some notifications may have failed.")
        print("   Check backend logs for details.")
        print("   Verify Twilio credentials are configured.")
    
    print("\n" + "="*60)
    print("  Test complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
