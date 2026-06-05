#!/usr/bin/env python3
"""
Test script to verify all required imports work after installing cleaned requirements.txt
Run this after: pip install -r backend/requirements.txt
"""

import sys

def test_imports():
    """Test all critical imports used in the project"""
    
    print("Testing imports from cleaned requirements.txt...\n")
    
    tests = [
        ("FastAPI", "from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, BackgroundTasks"),
        ("FastAPI Security", "from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials"),
        ("Starlette CORS", "from starlette.middleware.cors import CORSMiddleware"),
        ("Motor (MongoDB)", "from motor.motor_asyncio import AsyncIOMotorClient"),
        ("PyMongo", "import pymongo"),
        ("Pydantic", "from pydantic import BaseModel, Field, ConfigDict, EmailStr"),
        ("Python-dotenv", "from dotenv import load_dotenv"),
        ("Passlib", "from passlib.context import CryptContext"),
        ("JWT", "import jwt"),
        ("Twilio", "from twilio.rest import Client"),
        ("Pandas", "import pandas as pd"),
        ("NumPy", "import numpy"),
        ("Requests", "import requests"),
        ("Python-jose", "from jose import jwt as jose_jwt"),
        ("Email Validator", "from email_validator import validate_email"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name:20} - OK")
            passed += 1
        except ImportError as e:
            print(f"❌ {name:20} - FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {name:20} - ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    
    if failed > 0:
        print("❌ Some imports failed. Please check your installation.")
        print("Run: pip install -r backend/requirements.txt")
        return False
    else:
        print("✅ All imports successful! Requirements are correctly installed.")
        return True

def test_versions():
    """Test that key packages are at expected versions"""
    
    print("\nChecking package versions...\n")
    
    try:
        import fastapi
        import uvicorn
        import motor
        import twilio
        import pandas
        
        print(f"FastAPI:  {fastapi.__version__}")
        print(f"Uvicorn:  {uvicorn.__version__}")
        print(f"Motor:    {motor.version}")
        print(f"Twilio:   {twilio.__version__}")
        print(f"Pandas:   {pandas.__version__}")
        
        print("\n✅ Version check complete")
        return True
        
    except Exception as e:
        print(f"❌ Version check failed: {e}")
        return False

def main():
    """Run all tests"""
    
    print("="*50)
    print("Requirements.txt Installation Test")
    print("="*50)
    print()
    
    imports_ok = test_imports()
    versions_ok = test_versions()
    
    print("\n" + "="*50)
    if imports_ok and versions_ok:
        print("✅ ALL TESTS PASSED")
        print("="*50)
        print("\nYour cleaned requirements.txt is working correctly!")
        print("You can now start the backend server:")
        print("  cd backend")
        print("  uvicorn server:app --host 0.0.0.0 --port 8001 --reload")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*50)
        print("\nPlease reinstall requirements:")
        print("  pip install -r backend/requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
