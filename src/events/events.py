"""Event definitions for the email system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
import uuid


@dataclass
class Event:
    """Base event class."""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    aggregate_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "metadata": self.metadata,
        }


@dataclass
class UserCreated(Event):
    """Event triggered when a new user is created."""
    
    def __init__(
        self,
        user_id: int,
        login: str,
        first_name: str,
        last_name: str,
        created_at: datetime,
        metadata: Dict[str, Any] = None,
    ):
        super().__init__(
            event_type="UserCreated",
            aggregate_id=f"user-{user_id}",
            payload={
                "id": user_id,
                "login": login,
                "firstName": first_name,
                "lastName": last_name,
                "createdAt": created_at.isoformat() if isinstance(created_at, datetime) else str(created_at),
            },
            metadata=metadata or {"service": "email-api", "version": "1.0.0"},
        )


@dataclass
class FolderCreated(Event):
    """Event triggered when a new folder is created."""
    
    def __init__(
        self,
        folder_id: int,
        name: str,
        user_id: int,
        created_at: datetime,
        metadata: Dict[str, Any] = None,
    ):
        super().__init__(
            event_type="FolderCreated",
            aggregate_id=f"folder-{folder_id}",
            payload={
                "id": folder_id,
                "name": name,
                "userId": user_id,
                "createdAt": created_at.isoformat() if isinstance(created_at, datetime) else str(created_at),
            },
            metadata=metadata or {"service": "email-api", "version": "1.0.0"},
        )


@dataclass
class MessageCreated(Event):
    """Event triggered when a new message is created."""
    
    def __init__(
        self,
        message_id: int,
        subject: str,
        sender: str,
        recipient: str,
        folder_id: int,
        created_at: datetime,
        metadata: Dict[str, Any] = None,
    ):
        super().__init__(
            event_type="MessageCreated",
            aggregate_id=f"message-{message_id}",
            payload={
                "id": message_id,
                "subject": subject,
                "sender": sender,
                "recipient": recipient,
                "folderId": folder_id,
                "createdAt": created_at.isoformat() if isinstance(created_at, datetime) else str(created_at),
            },
            metadata=metadata or {"service": "email-api", "version": "1.0.0"},
        )
