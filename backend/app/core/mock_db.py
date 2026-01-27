from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class MockDB:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.devices: Dict[str, List[Dict[str, Any]]] = {}
        self.biomarkers: Dict[str, List[Dict[str, Any]]] = {}
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.consent: Dict[str, Dict[str, Any]] = {}
        self.manual_entries: Dict[str, List[Dict[str, Any]]] = {}
        self._seed_sample_data()
    
    def _seed_sample_data(self):
        self.users["user123"] = {
            "uid": "user123",
            "email": "test@pulselink.com",
            "role": "user",
            "age": 25,
            "gender": "male",
            "language": "en",
            "emergency_contacts": [{"name": "John Doe", "phone": "+971501234567"}],
            "created_at": "2025-01-20T10:00:00",
            "updated_at": "2025-01-26T14:30:00"
        }
        
        self.devices["user123"] = [
            {
                "device_id": "apple_watch_001",
                "device_name": "Apple Watch Series 8",
                "device_type": "smartwatch",
                "connected_at": "2025-01-20T10:00:00",
                "last_sync": "2025-01-26T14:30:00",
                "is_active": True,
                "brand": "Apple"
            },
            {
                "device_id": "fitbit_charge_5",
                "device_name": "Fitbit Charge 5",
                "device_type": "fitness_tracker",
                "connected_at": "2025-01-22T15:00:00",
                "last_sync": "2025-01-26T12:15:00",
                "is_active": True,
                "brand": "Fitbit"
            }
        ]
        
        self.manual_entries["user123"] = [
            {
                "entry_id": "entry_001",
                "biomarker_type": "blood_pressure",
                "value": {"systolic": 120, "diastolic": 80},  #this is BP like 120/80 mmHg
                "timestamp": "2025-01-26T09:00:00",
                "notes": "Morning reading"
            },
            {
                "entry_id": "entry_002",
                "biomarker_type": "mood",
                "value": "energetic",
                "timestamp": "2025-01-26T10:30:00",
                "notes": "After morning workout"
            }
        ]
        
        self.biomarkers["user123"] = [
            {
                "timestamp": "2025-01-26T14:30:00",
                "heart_rate": 72,
                "steps": 8432,
                "calories": 312.5,
                "source": "apple_watch_001"
            },
            {
                "timestamp": "2025-01-26T13:00:00",
                "heart_rate": 68,
                "steps": 5421,
                "calories": 198.3,
                "source": "apple_watch_001"
            }
        ]
        
        self.providers["provider456"] = {
            "uid": "provider456",
            "email": "dr.smith@hospital.com", #double check clash in db maybe?
            "role": "healthcare_provider",
            "name": "Dr. Sarah Smith",
            "license": "12345",          #was this how we're approving?
            "patients": ["user123"],
            "created_at": "2025-01-15T08:00:00"
        }
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        return self.users.get(uid)
    
    def update_user(self, uid: str, user_data: Dict[str, Any]) -> bool:
        if uid in self.users:
            self.users[uid].update(user_data)
            self.users[uid]["updated_at"] = datetime.now().isoformat()
            return True
        return False
    
    def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        return self.devices.get(user_id, [])
    
    def add_device(self, user_id: str, device_data: Dict[str, Any]) -> str:
        if user_id not in self.devices:
            self.devices[user_id] = []
        device_id = device_data.get("device_id", f"device_{uuid.uuid4().hex[:8]}")
        device_data["device_id"] = device_id
        device_data["connected_at"] = datetime.now().isoformat()
        device_data["last_sync"] = datetime.now().isoformat()
        self.devices[user_id].append(device_data)
        return device_id
    
    def get_manual_entries(self, user_id: str) -> List[Dict[str, Any]]:
        return self.manual_entries.get(user_id, [])
    
    def add_manual_entry(self, user_id: str, entry_data: Dict[str, Any]) -> str:
        if user_id not in self.manual_entries:
            self.manual_entries[user_id] = []
        entry_id = f"entry_{uuid.uuid4().hex[:8]}"
        entry_data["entry_id"] = entry_id
        if "timestamp" not in entry_data:
            entry_data["timestamp"] = datetime.now().isoformat()
        self.manual_entries[user_id].append(entry_data)
        return entry_id
    
    def get_real_time_data(self, user_id: str) -> List[Dict[str, Any]]:
        return self.biomarkers.get(user_id, [])[:5]

mock_db = MockDB()