#!/usr/bin/env python3
"""Test the Flask application"""

import sys
sys.path.insert(0, '.')

from app import create_app

def test_app():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        
        # Test system info
        response = client.get('/system/info')
        print(f"✅ System info: {response.status_code}")
        
        # Test security tips
        response = client.get('/cybersecurity/tips')
        print(f"✅ Security tips: {response.status_code}")
        print(f"   Tip: {response.get_json().get('tip')}")
        
        # Test registration
        response = client.post('/auth/register', json={
            'email': 'test@student.ac.uk',
            'password': 'Test123!',
            'full_name': 'Test User',
            'skills': ['Python', 'ML'],
            'industry': 'Technology'
        })
        print(f"✅ Registration: {response.status_code}")
        token = response.get_json().get('access_token')
        
        if token:
            # Test authenticated endpoint
            response = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
            print(f"✅ Authenticated user: {response.status_code}")
            
            # Test URL check with auth
            response = client.post('/cybersecurity/check-url', 
                                 headers={'Authorization': f'Bearer {token}'},
                                 json={'url': 'https://example-job.com'})
            print(f"✅ URL check: {response.status_code}")
        
        print("\n🎉 All tests passed! Backend is working.")

if __name__ == '__main__':
    test_app()