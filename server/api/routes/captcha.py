from io import BytesIO

from captcha.image import ImageCaptcha
from fastapi import APIRouter, Depends, HTTPException
from utils.random_text import get_random_text
import base64
from models import CaptchaCreate, CaptchaPublic, CaptchaData, GenSession
from sqlmodel import Session, select
from database import get_session
import uuid
import time

captcha = ImageCaptcha()

router = APIRouter()


def create_b64_captcha_image(chars: str) -> str:
    data: BytesIO = captcha.generate(chars)
    data.seek(0)
    return "data:image/png;base64," + base64.b64encode(data.read()).decode()


@router.post("/", response_model=CaptchaPublic)
def get_captcha(*, session: Session = Depends(get_session), body: CaptchaCreate):
    session_id = body.session_id

    statement = select(CaptchaData).where(CaptchaData.session_id == session_id)
    captcha_data = session.exec(statement).first()

    if not captcha_data:
        raise HTTPException(404)

    random_text = get_random_text()

    captcha_data.captcha_text = random_text
    captcha_data.valid = True
    captcha_data.update_time = time.time()

    session.add(captcha_data)
    session.commit()

    b64_data = create_b64_captcha_image(random_text)

    return CaptchaPublic(b64=b64_data, session_id=session_id)


@router.get("/session", response_model=GenSession)
def gen_session(*, session: Session = Depends(get_session)):
    session_id: uuid.UUID = uuid.uuid4()
    _captcha = CaptchaData(session_id=session_id)
    session.add(_captcha)
    session.commit()

    return GenSession(session_id=session_id)
