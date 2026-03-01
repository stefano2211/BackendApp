from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm # Removing form-data dependency
from sqlalchemy.orm import Session
from api import deps
from domain.schemas.user import UserCreate, UserLogin, UserResponse, Token, PasswordResetRequest, PasswordResetConfirm
from persistencia.repositories.user import UserRepository
from core.security import create_access_token, verify_password, get_password_hash
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    repo = UserRepository(db)
    if repo.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if repo.get_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    return repo.create(user_in)

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(deps.get_db)):
    repo = UserRepository(db)
    
    user = repo.get_by_username(login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(deps.get_db)):
    repo = UserRepository(db)
    user = repo.get_by_email(request.email)
    if not user:
        # Don't reveal if user exists for security
        return {"message": "Recovery email sent if account exists"}
    
    # Generate a temporary token (reusing JWE logic for simplicity)
    token = create_access_token(data={"sub": user.username, "purpose": "reset"}, expires_delta=timedelta(minutes=15))
    
    # MOCK: In a real app, send actual email
    print(f"DEBUG: Password reset token for {user.email}: {token}")
    
    return {"message": "Recovery email sent", "recovery_token": token}

@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(deps.get_db)):
    from core.security import decode_access_token
    payload = decode_access_token(request.token)
    if not payload or payload.get("purpose") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    repo = UserRepository(db)
    user = repo.get_by_username(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    repo.update_password(user, request.new_password)
    return {"message": "Password updated successfully"}
