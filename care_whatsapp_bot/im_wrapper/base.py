from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class MessageType(Enum):
    """Enumeration of supported message types"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"


@dataclass
class IMMessage:
    """Standardized incoming message format"""
    sender_id: str
    message_type: MessageType
    content: str
    platform: str
    timestamp: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class IMResponse:
    """Standardized outgoing message format"""
    recipient_id: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseIMProvider(ABC):
    """Abstract base class for instant messaging providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform_name = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name (e.g., 'whatsapp', 'telegram')"""
        pass
    
    @abstractmethod
    def parse_incoming_message(self, raw_data: Dict[str, Any]) -> Optional[IMMessage]:
        """Parse platform-specific webhook payload to standardized message format"""
        pass
    
    @abstractmethod
    def send_message(self, response: IMResponse) -> bool:
        """Send message via platform API"""
        pass
    
    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature (optional, platform-specific)"""
        return True
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information (optional)"""
        return {}