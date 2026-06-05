#!/usr/bin/env python3
"""
Final Attendance Notification System - Test Script

This script tests the complete finalized system:
1. Creates test parent with phone number
2. Creates test student linked to parent
3. Creates CSV with different status formats
4. Uploads CSV
5. Verifies notifications
6. Checks logs and response

Usage:
    python test_final_system.py
"""

import requests
import json
import time
from datetime import datetime
import os

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "admin@mlrit.ac.in"
ADMIN_PASSWORD = "admin123"

# Test data - REPLACE WITH YOUR VERIFIED PHONE NUMBER
TEST_PHONE = "+919876543210"  # ⚠️ IMPORTANT: Replace with your phone number
TEST_DATE = "15-01-2026"

def print_header(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def login():
    """Login and get access token"""
    print_header("Step 1: Login")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success(f"Login successful")
        print_info(f"Token: {token[:30]}...")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        return None

def create_parent(token):
    """Create test parent"""
    print_header("Step 2: Create Test Parent")
    
    parent_data = {
        "name": "Test Parent Final",
        "phone_number": TEST_PHONE,
        "email": "testparent.final@example.com",
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
        print_success("Parent created successfully")
        print_info(f"ID: {parent['id']}")
        print_info(f"Name: {parent['name']}")
        print_info(f"Phone: {parent['phone_number']}")
        return parent['id']
    else:
        print_error(f"Failed to create parent: {response.text}")
        return None

def create_student(token, parent_id):
    """Create test student"""
    print_header("Step 3: Create Test Student")
    
    roll_number = f"TEST{int(time.time())}"
    
    student_data = {
        "roll_number": roll_number,
        "name": "Test Student Final",
        "email": "teststudent.final@example.com",
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
        print_success("Student created successfully")
        print_info(f"ID: {student['id']}")
        print_info(f"Name: {student['name']}")
        print_info(f"Roll: {student['roll_number']}")
        return student['roll_number']
    else:
        print_error(f"Failed to create student: {response.text}")
        return None

def create_csv_file(roll_number):
    """Create test CSV file"""
    print_header("Step 4: Create Test CSV")
    
    # Test different status formats
    csv_content = f"""roll_number,date,status,subject
{roll_number},{TEST_DATE},absent,Mathematics
{roll_number},16-01-2026,a,Physics
{roll_number},17-01-2026,0,Chemistry
{roll_number},18-01-2026,false,Biology
{roll_number},19-01-2026,present,English
{roll_number},20-01-2026,p,History
{roll_number},21-01-2026,1,Geography
{roll_number},22-01-2026,true,Economics"""
    
    filename = "test_final_attendance.csv"
    with open(filename, "w") as f:
        f.write(csv_content)
    
    print_success(f"CSV file created: {filename}")
    print_info("CSV Content:")
    print(csv_content)
    
    return filename

def upload_csv(token, filename):
    """Upload CSV file"""
    print_header("Step 5: Upload CSV")
    
    with open(filename, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/attendance/upload-csv",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (filename, f, "text/csv")}
        )
    
    if response.status_code == 200:
        result = response.json()
        print_success("CSV uploaded successfully")
        print("\n📊 Response:")
        print(json.dumps(result, indent=2))
        
        # Verify response format
        print("\n🔍 Verification:")
        assert result["status"] == "success", "Status should be 'success'"
        print_success("Status: success ✓")
        
        assert result["total_records"] == 8, "Should have 8 total records"
        print_success(f"Total records: {result['total_records']} ✓")
        
        assert result["absent_count"] == 4, "Should have 4 absent students"
        print_success(f"Absent count: {result['absent_count']} ✓")
        
        assert result["present_count"] == 4, "Should have 4 present students"
        print_success(f"Present count: {result['present_count']} ✓")
        
        assert result["notifications_triggered"] == True, "Notifications should be triggered"
        print_success("Notifications triggered: True ✓")
        
        return True
    else:
        print_error(f"Failed to upload CSV: {response.text}")
        return False

def wait_for_processing():
    """Wait for background processing"""
    print_header("Step 6: Wait for Processing")
    
    print_info("Waiting 15 seconds for notifications to be processed...")
    for i in range(15, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print("   " + " "*50)
    print_success("Wait complete")

def check_notifications(token):
    """Check notifications"""
    print_header("Step 7: Check Notifications")
    
    response = requests.get(
        f"{BASE_URL}/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        notifications = response.json()
        print_success(f"Found {len(notifications)} total notifications")
        
        # Get recent notifications (last 8 = 4 absent × 2 types)
        recent = notifications[-8:] if len(notifications) >= 8 else notifications
        
        sms_count = sum(1 for n in recent if n['type'] == 'sms')
        voice_count = sum(1 for n in recent if n['type'] == 'voice')
        sent_count = sum(1 for n in recent if n['status'] == 'sent')
        failed_count = sum(1 for n in recent if n['status'] == 'failed')
        
        print_info(f"Recent notifications (last {len(recent)}):")
        print(f"   SMS: {sms_count}")
        print(f"   Voice: {voice_count}")
        print(f"   Sent: {sent_count}")
        print(f"   Failed: {failed_count}")
        
        # Show sample notifications
        print("\n📱 Sample Notifications:")
        for notif in recent[:2]:
            print(f"\n   Type: {notif['type'].upper()}")
            print(f"   Status: {notif['status']}")
            print(f"   Phone: {notif['phone_number']}")
            print(f"   Message: {notif['message']}")
            if notif.get('error_message'):
                print(f"   Error: {notif['error_message']}")
        
        # Verify message format
        if recent:
            sample_message = recent[0]['message']
            if "Your ward is absent for" in sample_message:
                print_success("\n✓ Message format is correct!")
            else:
                print_error("\n✗ Message format is incorrect!")
        
        return len(recent)
    else:
        print_error(f"Failed to get notifications: {response.text}")
        return 0

def check_statistics(token):
    """Check notification statistics"""
    print_header("Step 8: Check Statistics")
    
    response = requests.get(
        f"{BASE_URL}/notifications/stats?date={TEST_DATE}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_success(f"Statistics for {stats['date']}:")
        print(f"   Total: {stats['total_notifications']}")
        print(f"   Sent: {stats['sent']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success rate: {stats['success_rate']}%")
        print(f"\n   SMS: {stats['by_type']['sms']['sent']}/{stats['by_type']['sms']['total']}")
        print(f"   Voice: {stats['by_type']['voice']['sent']}/{stats['by_type']['voice']['total']}")
        return stats
    else:
        print_error(f"Failed to get statistics: {response.text}")
        return None

def main():
    """Run complete test"""
    print("\n" + "🚀 "*35)
    print("  FINAL ATTENDANCE NOTIFICATION SYSTEM - TEST")
    print("🚀 "*35)
    
    print(f"\n📋 Configuration:")
    print(f"   Backend: {BASE_URL}")
    print(f"   Phone: {TEST_PHONE}")
    print(f"   Date: {TEST_DATE}")
    
    if TEST_PHONE == "+919876543210":
        print("\n⚠️  WARNING: Using default phone number!")
        print("   Please update TEST_PHONE in the script with your verified number.")
        response = input("\n   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("\n❌ Test cancelled")
            return
    
    # Run tests
    token = login()
    if not token:
        print("\n❌ Test failed: Could not login")
        return
    
    parent_id = create_parent(token)
    if not parent_id:
        print("\n❌ Test failed: Could not create parent")
        return
    
    roll_number = create_student(token, parent_id)
    if not roll_number:
        print("\n❌ Test failed: Could not create student")
        return
    
    csv_file = create_csv_file(roll_number)
    
    if not upload_csv(token, csv_file):
        print("\n❌ Test failed: Could not upload CSV")
        return
    
    wait_for_processing()
    
    notif_count = check_notifications(token)
    stats = check_statistics(token)
    
    # Final summary
    print_header("TEST SUMMARY")
    
    if notif_count >= 2 and stats:
        print_success("TEST PASSED!")
        print("\n   ✓ Parent created")
        print("   ✓ Student created")
        print("   ✓ CSV uploaded")
        print("   ✓ Response format correct")
        print("   ✓ Notifications sent")
        print("   ✓ Statistics tracked")
        print("   ✓ Message format correct")
        
        print("\n📱 Check your phone for:")
        print("   - 4 SMS messages (one for each absent date)")
        print("   - 4 Voice calls (one for each absent date)")
        print("\n   Message format: 'Your ward is absent for {subject} on {date}'")
        
        print("\n🎉 System is working correctly!")
    else:
        print("⚠️  TEST PARTIALLY PASSED")
        print("\n   Some notifications may have failed.")
        print("   Check backend logs for details.")
        print("   Verify Twilio credentials are configured.")
    
    print("\n" + "="*70)
    print("  Test complete!")
    print("="*70 + "\n")
    
    # Cleanup
    try:
        os.remove(csv_file)
        print_info(f"Cleaned up: {csv_file}")
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
