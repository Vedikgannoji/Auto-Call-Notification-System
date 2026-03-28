import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if admin exists
    existing = await db.admin_users.find_one({"email": "admin@mlrit.ac.in"})
    
    if existing:
        print("Admin user already exists!")
        client.close()
        return
    
    # Create admin
    admin = {
        "id": str(uuid.uuid4()),
        "email": "admin@mlrit.ac.in",
        "full_name": "MLR Admin",
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.admin_users.insert_one(admin)
    print("✓ Admin user created successfully!")
    print(f"  Email: admin@mlrit.ac.in")
    print(f"  Password: admin123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
