from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class ResetTokenStatus(BaseModel):
    valid: bool
    email: str
