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
        self.linked_providers: Dict[str, List[Dict[str, Any]]] = {}
        self.social_shares: Dict[str, List[Dict[str, Any]]] = {}
        self.appointments: Dict[str, List[Dict[str, Any]]] = {}
        self.support_tickets: Dict[str, List[Dict[str, Any]]] = {}
        self.patient_alerts: Dict[str, List[Dict[str, Any]]] = {}
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
        
        self.patient_alerts["provider456"] = [
            {
                "alert_id": "prov_alert_1",
                "patient_id": "user123",
                "biomarker_type": "heart_rate",
                "condition": "greater_than",
                "threshold": 150,
                "enabled": True,
                "message": "high heart rate for patient user123",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        self.linked_providers["user123"] = [
            {"link_id": "link_google", "provider": "google", "external_id": "google-123", "linked_at": datetime.now().isoformat()}
        ]
        
        self.social_shares["user123"] = [
            {"share_id": "share1", "platform": "twitter", "metric": "steps", "message": "walked 10k", "created_at": datetime.now().isoformat()}
        ]
        
        self.appointments["user123"] = [
            {
                "appointment_id": "appt1",
                "provider_id": "provider456",
                "patient_id": "user123",
                "scheduled_for": datetime.now().isoformat(),
                "note": "general checkup",
                "reminder_minutes_before": 60,
                "status": "scheduled"
            }
        ]
        
        self.support_tickets["user123"] = [
            {"ticket_id": "ticket1", "subject": "login help", "message": "reset password not working", "status": "open", "created_at": datetime.now().isoformat()}
        ]
    
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
    
    def add_provider_link(self, user_id: str, link: Dict[str, Any]) -> str:
        if user_id not in self.linked_providers:
            self.linked_providers[user_id] = []
        link_id = f"link_{uuid.uuid4().hex[:8]}"
        link["link_id"] = link_id
        self.linked_providers[user_id].append(link)
        return link_id
    
    def get_provider_links(self, user_id: str) -> List[Dict[str, Any]]:
        return self.linked_providers.get(user_id, [])
    
    def delete_provider_link(self, link_id: str) -> bool:
        for user_id, links in self.linked_providers.items():
            for link in links:
                if link.get("link_id") == link_id:
                    links.remove(link)
                    return True
        return False
    
    def add_social_share(self, user_id: str, share: Dict[str, Any]) -> str:
        if user_id not in self.social_shares:
            self.social_shares[user_id] = []
        share_id = f"share_{uuid.uuid4().hex[:8]}"
        share["share_id"] = share_id
        self.social_shares[user_id].append(share)
        return share_id
    
    def get_social_shares(self, user_id: str) -> List[Dict[str, Any]]:
        return self.social_shares.get(user_id, [])
    
    def add_appointment(self, appointment: Dict[str, Any]) -> str:
        pid = appointment.get("patient_id")
        if not pid:
            return ""
        if pid not in self.appointments:
            self.appointments[pid] = []
        appointment_id = f"appt_{uuid.uuid4().hex[:8]}"
        appointment["appointment_id"] = appointment_id
        self.appointments[pid].append(appointment)
        return appointment_id
    
    def get_appointments(self, user_id: str) -> List[Dict[str, Any]]:
        return self.appointments.get(user_id, [])
    
    def add_support_ticket(self, user_id: str, ticket: Dict[str, Any]) -> str:
        if user_id not in self.support_tickets:
            self.support_tickets[user_id] = []
        ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"
        ticket["ticket_id"] = ticket_id
        self.support_tickets[user_id].append(ticket)
        return ticket_id
    
    def get_support_tickets(self, user_id: str) -> List[Dict[str, Any]]:
        return self.support_tickets.get(user_id, [])
    
    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        return self.providers.get(provider_id)
    
    def add_patient(self, provider_id: str, patient_id: str) -> bool:
        if provider_id not in self.providers:
            return False
        patients = self.providers[provider_id].setdefault("patients", [])
        if patient_id not in patients:
            patients.append(patient_id)
        return True
    
    def get_patients(self, provider_id: str) -> List[Dict[str, Any]]:
        prov = self.providers.get(provider_id, {})
        return prov.get("patients", [])
    
    def add_patient_alert(self, provider_id: str, alert: Dict[str, Any]) -> str:
        if provider_id not in self.patient_alerts:
            self.patient_alerts[provider_id] = []
        alert_id = f"prov_alert_{uuid.uuid4().hex[:8]}"
        alert["alert_id"] = alert_id
        self.patient_alerts[provider_id].append(alert)
        return alert_id
    
    def get_patient_alerts(self, provider_id: str) -> List[Dict[str, Any]]:
        return self.patient_alerts.get(provider_id, [])

mock_db = MockDB()
