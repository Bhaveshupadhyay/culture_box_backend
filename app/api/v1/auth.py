from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, User
from app.schemas.token import Token, RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm
from app.core.dependencies import get_auth_service, get_user_service
from app.services.auth import AuthService
from app.services.user import UserService
from app.core.exceptions import UnauthorizedException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class EmailVerificationRequest(BaseModel):
    token: str

def dummy_send_email(email: str, subject: str, body: str):
    # Dummy function to simulate sending email
    print(f"Sending email to {email}: {subject}")

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user."""
    user = await auth_service.register(user_in)
    token = auth_service.generate_email_verification_token(user.id)
    background_tasks.add_task(dummy_send_email, user.email, "Verify your email", f"Your token is {token}")
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = await auth_service.authenticate(email=form_data.username, password=form_data.password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    elif not user.is_active:
        raise UnauthorizedException("Inactive user")
    
    return auth_service.create_tokens(user.id)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh an access token using a refresh token."""
    return await auth_service.refresh(refresh_token=request.refresh_token)

@router.post("/verify-email")
async def verify_email(
    request: EmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify user's email with token."""
    await auth_service.verify_email(token=request.token)
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    """Request a password reset email."""
    user = await user_service.get_by_email(request.email)
    if user:
        token = auth_service.generate_password_reset_token(user.id)
        background_tasks.add_task(dummy_send_email, user.email, "Reset your password", f"Your token is {token}")
    return {"message": "If the email exists, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password with token."""
    await auth_service.reset_password(token=request.token, new_password=request.new_password)
    return {"message": "Password reset successfully"}
