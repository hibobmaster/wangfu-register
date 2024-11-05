from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException
from models import UserCreate, UserCreatePublic, CaptchaData
from sqlmodel import Session, select
from database import get_session
from utils.keycloak_api import (
    check_email_exist,
    check_username_exist,
    create_user,
    delete_user_by_username,
)
from keycloak import KeycloakDeleteError
from configs import captcha_session_timeout
import time
from utils.log import logger
import subprocess
from shlex import quote

router = APIRouter()


@router.post("/register", response_model=UserCreatePublic)
def register_user(*, session: Session = Depends(get_session), body: UserCreate):
    _email = body.email
    _username = body.username
    _password = body.password
    _session_id = body.session_id
    _captcha_code = body.code

    if check_email_exist(_email):
        return UserCreatePublic(ok=False, reason="邮箱已存在")

    if check_username_exist(_username):
        return UserCreatePublic(ok=False, reason="用户名已存在")

    if len(_password) <= 6:
        return UserCreatePublic(ok=False, reason="密码长度必须大于6")

    statement = select(CaptchaData).where(CaptchaData.session_id == _session_id)
    _captcha_data = session.exec(statement).first()

    if not _captcha_data:
        raise HTTPException(404, detail="session_id not found")

    if not _captcha_data.valid:
        return UserCreatePublic(ok=False, reason="验证码无效")

    if int(time.time() - _captcha_data.update_time) > captcha_session_timeout:
        _captcha_data.valid = False
        return UserCreatePublic(ok=False, reason="验证码过期")

    if _captcha_code.lower() != _captcha_data.captcha_text.lower():
        _captcha_data.valid = False
        return UserCreatePublic(ok=False, reason="验证码错误")

    _captcha_data.valid = False
    session.add(_captcha_data)
    session.commit()

    try:
        create_user(username=_username, password=_password, email=_email)
    except Exception as e:
        logger.error(e)
        return UserCreatePublic(ok=False, reason=e)

    try:
        # docker exec -it dms setup email add <EMAIL ADDRESS> [<PASSWORD>]
        subprocess.check_output(
            [
                "docker",
                "exec",
                "-it",
                "dms",
                "setup",
                "email",
                "add",
                _email,
                quote(_password),
            ],
        )
    except Exception as e:
        try:
            delete_user_by_username(_username)
        except KeycloakDeleteError as e2:
            logger.error(e2)

        logger.error(e)
        return UserCreatePublic(ok=False, reason="邮箱账号创建失败，请联系管理员")

    return UserCreatePublic(ok=True, reason=None)
