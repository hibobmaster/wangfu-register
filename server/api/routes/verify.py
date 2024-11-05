from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import (
    UserExistPublic,
    UserExistCheck,
    EmailExistPublic,
    EmailExistCheck,
    CaptchaVerify,
    CaptchaVerifyResponse,
    CaptchaData,
)
from utils.keycloak_api import check_email_exist, check_username_exist
from constants import reserved_usernames, reserved_emails
from configs import allow_email_hostnames, captcha_session_timeout
import time

router = APIRouter()


@router.post("/username", response_model=UserExistPublic)
def verify_username(body: UserExistCheck):
    username = body.username
    if username in reserved_usernames:
        return UserExistPublic(username=username, exist=True)
    result = check_username_exist(username)
    return UserExistPublic(username=username, exist=result)


@router.post("/email", response_model=EmailExistPublic)
def verify_email(body: EmailExistCheck):
    email = body.email
    if email in reserved_emails:
        return EmailExistPublic(email=email, exist=True)
    elif email.split("@")[1] not in allow_email_hostnames:
        return EmailExistPublic(email=email, exist=True)
    result = check_email_exist(email)
    return EmailExistPublic(email=email, exist=result)


@router.post("/captcha", response_model=CaptchaVerifyResponse)
def verify_captcha(*, session: Session = Depends(get_session), body: CaptchaVerify):
    code = body.code.lower()
    session_id = body.session_id
    statement = select(CaptchaData).where(CaptchaData.session_id == session_id)
    _captcha = session.exec(statement=statement).first()
    if not _captcha:
        raise HTTPException(404)
    elif code != _captcha.captcha_text.lower():
        return CaptchaVerifyResponse(ok=False, reason="invalid")
    elif int(time.time() - _captcha.update_time) > captcha_session_timeout:
        return CaptchaVerifyResponse(ok=False, reason="expire")

    return CaptchaVerifyResponse(ok=True, reason=None)
