#!/usr/bin/env python3
# quick check if server modules load correctly

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    # test mock db
    from app.core.mock_db import mock_db
    user = mock_db.get_user('user123')
    print(f"Mock DB: OK ({user['email']})")
    
    # test main app import
    from app.main import app
    print("FastAPI app: OK")
    
    print()
    print("All imports working. Server should start.")
    print("Run: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
