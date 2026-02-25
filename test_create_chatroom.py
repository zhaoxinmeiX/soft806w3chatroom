#!/usr/bin/env python3
"""
Test script for the create chatroom endpoint
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/auth"

def test_create_chatroom():
    """Test the create chatroom endpoint"""
    
    # First, login to get a token
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{BASE_URL}/login/", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print(f"Token obtained: {token[:20]}...")
            
            # Create chatroom
            headers = {
                "Authorization": f"Token {token}",
                "Content-Type": "application/json"
            }
            
            chatroom_data = {
                "name": "Test Chatroom",
                "description": "A test chatroom for testing",
                "is_private": False
            }
            
            create_response = requests.post(
                f"{BASE_URL}/chatrooms/", 
                json=chatroom_data, 
                headers=headers
            )
            
            print(f"Create Chatroom Status: {create_response.status_code}")
            print(f"Response: {json.dumps(create_response.json(), indent=2)}")
            
        else:
            print(f"Login failed: {login_response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Django server is running.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_chatroom()
