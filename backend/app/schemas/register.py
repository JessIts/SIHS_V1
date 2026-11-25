from pydantic import BaseModel, Field

from app.schemas.types import NormalizedEmail


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: NormalizedEmail

    phone: str = Field(
        min_length=7,
        max_length=20,
    )

    document_number: str = Field(
        min_length=5,
        max_length=30,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )
