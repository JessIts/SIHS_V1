from pydantic import BaseModel, Field

from app.schemas.types import NormalizedEmail


class ForgotPasswordRequest(BaseModel):
    email: NormalizedEmail


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class ResetTokenStatus(BaseModel):
    valid: bool
    email: str
