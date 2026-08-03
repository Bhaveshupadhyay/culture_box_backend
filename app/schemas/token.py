from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
    type: str | None = None
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
class PasswordResetRequest(BaseModel):
    email: str
    
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
