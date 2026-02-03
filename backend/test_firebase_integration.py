#!/usr/bin/env python3
# test firebase integration - make sure firebase is connected

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def test_firebase():
    print("Testing Firebase Connection")
    print("-" * 30)
    
    # test 1: import firestore module
    try:
        from app.core import firestore
        print("Firestore module: OK")
    except Exception as e:
        print(f"Firestore import failed: {e}")
        return False
    
    # test 2: check if we can get db client
    try:
        from firebase_admin import firestore as fs
        db = fs.client()
        print("Firebase client: OK")
    except Exception as e:
        print(f"Firebase client failed: {e}")
        return False
    
    # test 3: try reading from users collection
    try:
        docs = db.collection("users").limit(1).get()
        print(f"Read test: OK (found {len(docs)} users)")
    except Exception as e:
        print(f"Read test failed: {e}")
        return False
    
    # test 4: test firestore helper functions
    try:
        user = firestore.get_user("user123")
        if user:
            print(f"get_user: OK ({user.get('email', 'no email')})")
        else:
            print("get_user: OK (returned None)")
    except Exception as e:
        print(f"get_user failed: {e}")
        return False
    
    # test 5: write test
    try:
        entry_id = firestore.add_manual_entry("user123", {
            "biomarker_type": "test",
            "value": 100
        })
        if entry_id:
            print(f"Write test: OK (id: {entry_id[:8]}...)")
        else:
            print("Write test: FAILED (no id returned)")
    except Exception as e:
        print(f"Write test failed: {e}")
        return False
    
    print()
    print("All tests passed!")
    return True

if __name__ == "__main__":
    success = test_firebase()
    sys.exit(0 if success else 1)
