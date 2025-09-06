"""
User model and authentication utilities
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import hashlib

class User(BaseModel):
    """User model for authentication and profile management"""
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    name: str
    password_hash: Optional[str] = None
    google_id: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class UserCreate(BaseModel):
    """User creation schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response schema (without sensitive data)"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class GoogleUserInfo(BaseModel):
    """Google user info from OAuth"""
    sub: str  # Google user ID
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False

class UserSession(BaseModel):
    """User session model"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    session_token: str
    refresh_token: Optional[str] = None
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    import hashlib
    import secrets
    
    # Generate a random salt
    salt = secrets.token_hex(32)
    
    # Hash the password with salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Return salt + hash
    return salt + password_hash

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    if len(password_hash) < 64:
        return False
    
    # Extract salt and hash
    salt = password_hash[:64]
    stored_hash = password_hash[64:]
    
    # Hash the provided password with the same salt
    password_hash_check = hashlib.sha256((password + salt).encode()).hexdigest()
    
    return password_hash_check == stored_hash

def generate_gravatar_url(email: str, size: int = 80) -> str:
    """Generate Gravatar URL for user's email"""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon"

