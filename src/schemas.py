from pydantic import BaseModel, EmailStr, ConfigDict, Field


class ContactBase(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: str


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    avatar: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8,
                          description="New password (min 8 characters)")


class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    new_password: str = Field(..., min_length=8,
                              description="New password (min 8 characters)")
