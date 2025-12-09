"""
Week 11: Object-Oriented Programming (OOP) Design
Entity classes for the Multi-Domain Intelligence Platform.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class User:
    """Represents a user of the platform."""
    user_id: int
    username: str
    password_hash: str
    role: str  # admin, cybersecurity, datascience, it_operations
    created_at: datetime = field(default_factory=datetime.now)
    
    def has_access_to(self, domain: str) -> bool:
        """Check if user has access to a specific domain."""
        if self.role == 'admin':
            return True
        domain_map = {
            'cybersecurity': ['cybersecurity', 'admin'],
            'datascience': ['datascience', 'admin'],
            'it_operations': ['it_operations', 'admin']
        }
        return self.role in domain_map.get(domain, [])
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


@dataclass
class SecurityIncident:
    """Represents a cybersecurity incident."""
    incident_id: str
    title: str
    description: str
    threat_type: str  # Phishing, Malware, DDoS, etc.
    severity: str  # Critical, High, Medium, Low
    status: str  # Open, In Progress, Resolved
    assigned_to: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_time_hours: Optional[float] = None
    source_ip: Optional[str] = None
    target_system: Optional[str] = None
    
    def is_phishing(self) -> bool:
        """Check if this is a phishing incident."""
        return self.threat_type.lower() == 'phishing'
    
    def is_critical(self) -> bool:
        """Check if this is a critical severity incident."""
        return self.severity.lower() == 'critical'
    
    def is_resolved(self) -> bool:
        """Check if incident is resolved."""
        return self.status.lower() == 'resolved'
    
    def get_backlog_age_hours(self) -> float:
        """Calculate hours since creation if not resolved."""
        if self.is_resolved():
            return 0
        delta = datetime.now() - self.created_at
        return delta.total_seconds() / 3600
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'incident_id': self.incident_id,
            'title': self.title,
            'description': self.description,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at and isinstance(self.resolved_at, datetime) else self.resolved_at,
            'resolution_time_hours': self.resolution_time_hours,
            'source_ip': self.source_ip,
            'target_system': self.target_system
        }


@dataclass
class Dataset:
    """Represents a dataset in the data governance catalog."""
    dataset_id: str
    name: str
    description: str
    source_department: str
    file_format: str
    size_mb: float
    row_count: int
    column_count: int
    uploaded_by: str
    upload_date: datetime
    last_accessed: Optional[datetime] = None
    quality_score: float = 0.0
    status: str = "Active"  # Active, Archived, Deprecated
    storage_location: str = ""
    
    def needs_archiving(self, days_threshold: int = 90) -> bool:
        """Check if dataset should be archived based on last access."""
        if not self.last_accessed:
            return True
        delta = datetime.now() - self.last_accessed
        return delta.days > days_threshold
    
    def is_large_dataset(self, size_threshold_mb: float = 500) -> bool:
        """Check if this is considered a large dataset."""
        return self.size_mb >= size_threshold_mb
    
    def get_size_category(self) -> str:
        """Categorize dataset by size."""
        if self.size_mb < 100:
            return "Small"
        elif self.size_mb < 500:
            return "Medium"
        elif self.size_mb < 1000:
            return "Large"
        else:
            return "Very Large"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'dataset_id': self.dataset_id,
            'name': self.name,
            'description': self.description,
            'source_department': self.source_department,
            'file_format': self.file_format,
            'size_mb': self.size_mb,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'uploaded_by': self.uploaded_by,
            'upload_date': self.upload_date.isoformat() if isinstance(self.upload_date, datetime) else self.upload_date,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed and isinstance(self.last_accessed, datetime) else self.last_accessed,
            'quality_score': self.quality_score,
            'status': self.status,
            'storage_location': self.storage_location
        }


@dataclass
class ITTicket:
    """Represents an IT support ticket."""
    ticket_id: str
    title: str
    description: str
    category: str  # Hardware, Software, Network, Email, Account
    priority: str  # Critical, High, Medium, Low
    status: str  # Open, In Progress, Waiting for User, Resolved
    requester: str
    assigned_to: str
    created_at: datetime
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_time_hours: Optional[float] = None
    sla_met: Optional[bool] = None
    department: str = ""
    satisfaction_rating: Optional[int] = None
    
    def is_waiting_for_user(self) -> bool:
        """Check if ticket is in 'Waiting for User' status."""
        return self.status.lower() == 'waiting for user'
    
    def is_resolved(self) -> bool:
        """Check if ticket is resolved."""
        return self.status.lower() == 'resolved'
    
    def get_response_time_hours(self) -> Optional[float]:
        """Calculate time to first response in hours."""
        if not self.first_response_at:
            return None
        delta = self.first_response_at - self.created_at
        return delta.total_seconds() / 3600
    
    def get_age_hours(self) -> float:
        """Calculate ticket age in hours."""
        if self.is_resolved() and self.resolved_at:
            delta = self.resolved_at - self.created_at
        else:
            delta = datetime.now() - self.created_at
        return delta.total_seconds() / 3600
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'ticket_id': self.ticket_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'requester': self.requester,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'first_response_at': self.first_response_at.isoformat() if self.first_response_at and isinstance(self.first_response_at, datetime) else self.first_response_at,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at and isinstance(self.resolved_at, datetime) else self.resolved_at,
            'resolution_time_hours': self.resolution_time_hours,
            'sla_met': self.sla_met,
            'department': self.department,
            'satisfaction_rating': self.satisfaction_rating
        }


# Factory functions to create objects from database rows
def create_user_from_row(row: tuple) -> User:
    """Create User object from database row."""
    return User(
        user_id=row[0],
        username=row[1],
        password_hash=row[2],
        role=row[3],
        created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now()
    )


def create_incident_from_row(row: tuple) -> SecurityIncident:
    """Create SecurityIncident object from database row."""
    return SecurityIncident(
        incident_id=row[0],
        title=row[1],
        description=row[2],
        threat_type=row[3],
        severity=row[4],
        status=row[5],
        assigned_to=row[6],
        created_at=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
        resolved_at=datetime.fromisoformat(row[8]) if row[8] else None,
        resolution_time_hours=float(row[9]) if row[9] else None,
        source_ip=row[10],
        target_system=row[11]
    )


def create_dataset_from_row(row: tuple) -> Dataset:
    """Create Dataset object from database row."""
    return Dataset(
        dataset_id=row[0],
        name=row[1],
        description=row[2],
        source_department=row[3],
        file_format=row[4],
        size_mb=float(row[5]) if row[5] else 0,
        row_count=int(row[6]) if row[6] else 0,
        column_count=int(row[7]) if row[7] else 0,
        uploaded_by=row[8],
        upload_date=datetime.fromisoformat(row[9]) if row[9] else datetime.now(),
        last_accessed=datetime.fromisoformat(row[10]) if row[10] else None,
        quality_score=float(row[11]) if row[11] else 0,
        status=row[12] if row[12] else "Active",
        storage_location=row[13] if row[13] else ""
    )


def create_ticket_from_row(row: tuple) -> ITTicket:
    """Create ITTicket object from database row."""
    return ITTicket(
        ticket_id=row[0],
        title=row[1],
        description=row[2],
        category=row[3],
        priority=row[4],
        status=row[5],
        requester=row[6],
        assigned_to=row[7],
        created_at=datetime.fromisoformat(row[8]) if row[8] else datetime.now(),
        first_response_at=datetime.fromisoformat(row[9]) if row[9] else None,
        resolved_at=datetime.fromisoformat(row[10]) if row[10] else None,
        resolution_time_hours=float(row[11]) if row[11] else None,
        sla_met=row[12] == 'Yes' if row[12] else None,
        department=row[13] if row[13] else "",
        satisfaction_rating=int(row[14]) if row[14] else None
    )

