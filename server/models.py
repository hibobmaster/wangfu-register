from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr
import uuid
import time


class CaptchaCreate(BaseModel):
    session_id: uuid.UUID


class CaptchaPublic(BaseModel):
    b64: str
    session_id: uuid.UUID


class CaptchaVerify(BaseModel):
    session_id: uuid.UUID
    code: str


class CaptchaVerifyResponse(BaseModel):
    ok: bool
    reason: str | None


class CaptchaData(SQLModel, table=True):
    session_id: uuid.UUID = Field(primary_key=True)
    captcha_text: str | None = Field(default=None)
    valid: bool = Field(default=False)
    update_time: float = Field(default_factory=time.time)


class GenSession(BaseModel):
    session_id: uuid.UUID


class UserExist(BaseModel):
    username: str


class UserExistPublic(UserExist):
    exist: bool


class UserExistCheck(UserExist):
    pass


class EmailExist(BaseModel):
    email: EmailStr


class EmailExistPublic(EmailExist):
    exist: bool


class EmailExistCheck(EmailExist):
    pass


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    code: str
    session_id: uuid.UUID


class UserCreatePublic(BaseModel):
    ok: bool
    reason: str | None
