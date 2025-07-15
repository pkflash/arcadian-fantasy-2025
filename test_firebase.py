#!/usr/bin/env python3
"""
Test script to verify Firebase connectivity and basic operations
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def test_firebase_connection():
    """Test basic Firebase connection and operations"""
    try:
        # Initialize Firebase
        cred = credentials.Certificate('key.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        print("YES!")
        
        # Test writing to Firestore
        test_doc = db.collection('test').add({
            'message': 'Hello Firebase!',
            'timestamp': datetime.now()
        })
        print(f"Test document ID: {test_doc[1].id}")
        
        # Test reading from Firestore
        doc = db.collection('test').document(test_doc[1].id).get()
        if doc.exists:
            print(f"Test document: {doc.to_dict()}")
        
        # Clean up test document
        db.collection('test').document(test_doc[1].id).delete()
        print("Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"Firebase test failed: {e}")
        return False

def test_collections():
    """Test creating the required collections"""
    try:
        db = firestore.client()
        
        # Test users collection
        user_ref = db.collection('users').add({
            'email': 'test@example.com',
            'username': 'testuser',
            'created_at': datetime.now()
        })
        print(f"Users collection test: {user_ref[1].id}")
        
        # Test teams collection
        team_ref = db.collection('teams').add({
            'user_id': user_ref[1].id,
            'team_name': 'Test Team',
            'players': ['player1', 'player2'],
            'created_at': datetime.now()
        })
        print(f"Teams collection test: {team_ref[1].id}")
        
        # Test leaderboard collection
        leaderboard_ref = db.collection('leaderboard').add({
            'user_id': user_ref[1].id,
            'team_id': team_ref[1].id,
            'team_name': 'Test Team',
            'points': 100,
            'created_at': datetime.now()
        })
        print(f"Leaderboard collection test: {leaderboard_ref[1].id}")
        
        # Clean up test data
        db.collection('users').document(user_ref[1].id).delete()
        db.collection('teams').document(team_ref[1].id).delete()
        db.collection('leaderboard').document(leaderboard_ref[1].id).delete()
        print("Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"Collections test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Firebase setup...")
    print("=" * 40)
    
    if test_firebase_connection():
        print("\nTesting collections...")
        print("-" * 20)
        test_collections()
    
    print("\nFirebase setup is ready!") 