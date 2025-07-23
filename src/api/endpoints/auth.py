# src/api/endpoints/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta

from src.api.models import AuthRequest, TokenResponse
from src.api.auth import AuthService
from src.core.config import Settings

router = APIRouter()

# Simple user store (in production, use database)
USERS = {
    "admin": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
    "user1": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
}

@router.post("/login", response_model=TokenResponse)
async def login(request: AuthRequest):
    """Login to get JWT token"""
    auth_service = AuthService(Settings.from_env())
    
    # Check user exists and password is correct
    if request.username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not auth_service.verify_password(request.password, USERS[request.username]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = auth_service.create_access_token(
        data={"sub": request.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800
    )