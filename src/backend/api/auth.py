"""
Authentication API endpoints for user registration, login, and OAuth
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from models.user import (
    User, UserCreate, UserLogin, UserResponse, GoogleUserInfo, 
    UserSession, generate_gravatar_url
)
from utils.auth import auth_manager, get_current_user
from models.database import get_database

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Request/Response models
class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    """Google OAuth request model"""
    credential: str

class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes

# Helper functions
async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[Dict]:
    """Get user by email from database"""
    if db is None:
        return None
    
    try:
        user = await db.users.find_one({"email": email})
        return user
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        return None

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict]:
    """Get user by ID from database"""
    if db is None:
        return None
    
    try:
        from bson import ObjectId
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception as e:
        logger.error(f"Error fetching user by ID: {e}")
        return None

async def create_user(db: AsyncIOMotorDatabase, user_data: Dict) -> Optional[str]:
    """Create a new user in database"""
    if db is None:
        raise HTTPException(
            status_code=503, 
            detail="Database not available"
        )
    
    try:
        result = await db.users.insert_one(user_data)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=400, 
            detail="User with this email already exists"
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to create user"
        )

async def update_user_login(db: AsyncIOMotorDatabase, user_id: str):
    """Update user's last login timestamp"""
    if db is None:
        return
    
    try:
        from bson import ObjectId
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    except Exception as e:
        logger.error(f"Error updating user login: {e}")

def create_user_response(user_data: Dict) -> UserResponse:
    """Create UserResponse from database user data"""
    return UserResponse(
        id=str(user_data.get("_id")),
        email=user_data.get("email"),
        name=user_data.get("name"),
        picture=user_data.get("picture"),
        is_active=user_data.get("is_active", True),
        is_verified=user_data.get("is_verified", False),
        created_at=user_data.get("created_at", datetime.utcnow()),
        last_login=user_data.get("last_login"),
        profile=user_data.get("profile"),
        preferences=user_data.get("preferences")
    )

# Authentication endpoints
@router.post("/signup", response_model=AuthResponse)
async def signup(
    user_data: UserCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Register a new user"""
    try:
        # Check if user already exists
        if db is not None:
            existing_user = await get_user_by_email(db, user_data.email)
            if existing_user:
                return AuthResponse(
                    success=False,
                    message="User with this email already exists"
                )
        
        # Hash password
        password_hash = auth_manager.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "name": user_data.name,
            "password_hash": password_hash,
            "picture": generate_gravatar_url(user_data.email),
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "profile": {},
            "preferences": {}
        }
        
        # Create user in database
        if db is not None:
            user_id = await create_user(db, user_doc)
        else:
            # Fallback for when database is not available
            import uuid
            user_id = str(uuid.uuid4())
        
        # Create tokens
        token_data = {
            "sub": user_id,
            "email": user_data.email,
            "name": user_data.name
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Create user response
        user_doc["_id"] = user_id
        user_response = create_user_response(user_doc)
        
        # Update login timestamp
        if db is not None:
            await update_user_login(db, user_id)
        
        return AuthResponse(
            success=True,
            message="User created successfully",
            user=user_response,
            token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during signup"
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Login user with email and password"""
    try:
        # Get user from database
        if db is None:
            return AuthResponse(
                success=False,
                message="Database not available"
            )
            
        user = await get_user_by_email(db, user_credentials.email)
        if not user:
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Verify password
        if not user.get("password_hash"):
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        if not auth_manager.verify_password(user_credentials.password, user["password_hash"]):
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            return AuthResponse(
                success=False,
                message="Account is deactivated"
            )
        
        # Create tokens
        user_id = str(user["_id"])
        token_data = {
            "sub": user_id,
            "email": user["email"],
            "name": user["name"]
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Create user response
        user_response = create_user_response(user)
        
        # Update login timestamp
        await update_user_login(db, user_id)
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user=user_response,
            token=access_token,
            refresh_token=refresh_token
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during login"
        )

@router.post("/google", response_model=AuthResponse)
async def google_auth(
    google_request: GoogleAuthRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Authenticate user with Google OAuth"""
    try:
        # Verify Google token
        google_user_info = await auth_manager.verify_google_token(google_request.credential)
        if not google_user_info:
            return AuthResponse(
                success=False,
                message="Invalid Google token"
            )
        
        # Check if user exists
        user = None
        if db is not None:
            user = await get_user_by_email(db, google_user_info["email"])
        
        if user:
            # Update existing user with Google info
            user_id = str(user["_id"])
            update_data = {
                "google_id": google_user_info["google_id"],
                "picture": google_user_info.get("picture", user.get("picture")),
                "is_verified": google_user_info.get("email_verified", user.get("is_verified", False)),
                "updated_at": datetime.utcnow()
            }
            
            if db is not None:
                from bson import ObjectId
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
            
            # Update user dict for response
            user.update(update_data)
        else:
            # Create new user from Google info
            user_doc = {
                "email": google_user_info["email"],
                "name": google_user_info["name"],
                "google_id": google_user_info["google_id"],
                "picture": google_user_info.get("picture") or generate_gravatar_url(google_user_info["email"]),
                "is_active": True,
                "is_verified": google_user_info.get("email_verified", False),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "profile": {},
                "preferences": {}
            }
            
            if db is not None:
                user_id = await create_user(db, user_doc)
            else:
                # Fallback for when database is not available
                import uuid
                user_id = str(uuid.uuid4())
            user_doc["_id"] = user_id
            user = user_doc
        
        # Create tokens
        token_data = {
            "sub": str(user["_id"]),
            "email": user["email"],
            "name": user["name"]
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Create user response
        user_response = create_user_response(user)
        
        # Update login timestamp
        if db is not None:
            await update_user_login(db, str(user["_id"]))
        
        return AuthResponse(
            success=True,
            message="Google authentication successful",
            user=user_response,
            token=access_token,
            refresh_token=refresh_token
        )
        
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during Google authentication"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = auth_manager.verify_token(refresh_request.refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        
        # Get user from database to ensure they still exist and are active
        user = await get_user_by_id(db, user_id)
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=401,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        token_data = {
            "sub": user_id,
            "email": user["email"],
            "name": user["name"]
        }
        
        access_token = auth_manager.create_access_token(token_data)
        new_refresh_token = auth_manager.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during token refresh"
        )

@router.post("/logout")
async def logout(
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Logout user (invalidate tokens)"""
    try:
        # In a production system, you would add the token to a blacklist
        # For now, we just return success as the frontend will remove the token
        
        return {
            "success": True,
            "message": "Logout successful"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during logout"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user information"""
    try:
        # Get full user data from database
        user = await get_user_by_id(db, current_user["id"])
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return create_user_response(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/verify")
async def verify_token(current_user: Dict = Depends(get_current_user)):
    """Verify if current token is valid"""
    return {
        "valid": True,
        "user": current_user
    }

