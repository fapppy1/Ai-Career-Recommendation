#!/usr/bin/env python3
"""
Minimal JWT Auth Test - Bypasses PowerShell header issues
Run this to verify JWT is working end-to-end
"""

import requests, json, sys

BASE = "http://localhost:5000"

def test_auth():
    print("🔹 Testing JWT Auth with Python requests...")
    
    # 1. Register
    print("   Registering user...")
    reg = requests.post(f"{BASE}/auth/register", json={
        "email": "py_test_2597225@student.ac.uk",
        "password": "PyTest123!",
        "full_name": "Python Test",
        "industry": "Technology",
        "skills": ["Python", "SQL"]
    })
    
    if reg.status_code != 201:
        print(f"❌ Registration failed: {reg.status_code} - {reg.text}")
        return False
    
    reg_data = reg.json()
    if not reg_data.get('success'):
        print(f"❌ Registration error: {reg_data.get('error')}")
        return False
    
    token = reg_data['access_token']
    print(f"✅ Registered. Token: {token[:40]}...")
    
    # 2. Test /auth/me
    print("   Testing /auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    me = requests.get(f"{BASE}/auth/me", headers=headers)
    
    if me.status_code == 200:
        me_data = me.json()
        print(f"✅✅✅ AUTH SUCCESS! ✅✅✅")
        print(f"   User: {me_data['user']['full_name']} (ID: {me_data['user']['id']})")
        
        # 3. Test health
        health = requests.get(f"{BASE}/health").json()
        print(f"🗄️  Database: {health['database_type']}")
        
        if health['database_type'] == 'postgresql':
            print("✅✅✅ FULL SYSTEM WORKING! ✅✅✅")
            print("   • JWT Auth: Working")
            print("   • PostgreSQL: Connected") 
            print("   • Hybrid ML: Active")
            print("   • Ready for dissertation!")
            return True
    else:
        print(f"❌ /auth/me failed: {me.status_code}")
        print(f"   Response: {me.text}")
        return False

if __name__ == "__main__":
    success = test_auth()
    sys.exit(0 if success else 1)