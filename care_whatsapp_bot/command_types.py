from enum import Enum


class CommandType:
    
    
    LOGIN = "login"
    LOGOUT = "logout"
    VERIFY = "verify"
    
    MY_INFO = "my_info"
    MY_RECORDS = "my_records"
    MY_MEDICATIONS = "my_medications"
    MY_APPOINTMENTS = "my_appointments"
    BOOK_APPOINTMENT = "book_appointment"
    
    SEARCH_PATIENT = "search_patient"
    PATIENT_INFO = "patient_info"
    PATIENT_RECORDS = "patient_records"
    PATIENT_MEDICATIONS = "patient_medications"
    PATIENT_APPOINTMENTS = "patient_appointments"
    
    HELP = "help"
    STATUS = "status"
    MENU = "menu"
    
    PING = "ping"
    VERSION = "version"


class UserType:
    """Enumeration of user types"""
    PATIENT = "patient"
    STAFF = "staff"
    UNKNOWN = "unknown"


class MessageType:
    """Enumeration of WhatsApp message types"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    CONTACT = "contact"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"


class ConversationState:
    """Enumeration of conversation states"""
    INITIAL = "initial"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    WAITING_FOR_OTP = "waiting_for_otp"
    WAITING_FOR_INPUT = "waiting_for_input"
    PROCESSING = "processing"
    ERROR = "error"