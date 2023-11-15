import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
from keycloak import KeycloakAdmin, KeycloakGetError
from keycloak import KeycloakOpenIDConnection
from .log import getlogger
from .db import DBManager
import subprocess
import requests
from shlex import quote as shellquote

reserved_users = [
    "admin",
    "administrator",
    "root",
    "postmaster",
    "webmaster",
    "wf",
    "csu",
    "csuwf",
    "paper-server",
]

reserved_emails = [
    "admin@csuwf.com",
    "administrator@csuwf.com",
    "root@csuwf.com",
    "postmaster@csuwf.com",
    "webmaster@csuwf.com",
    "wf@csuwf.com",
    "csu@csuwf.com",
    "csuwf@csuwf.com",
    "rocketchat-bot@csuwf.com",
    "nextcloud-bot@csuwf.com",
    "dmarc.report@csuwf.com",
    "keycloak@csuwf.com",
    "wordpress-bot@csuwf.com",
    "discourse-bot@csuwf.com",
]

logger = getlogger()
dbmanager = DBManager()


class Register_Request_Body(BaseModel):
    username: str
    email: str
    password: str
    token: str


class Password_Reset_Request_Body(BaseModel):
    email: str
    password: str
    authcode: str
    token: str


class checkemailexistRequest(BaseModel):
    email: str


class checkusernameexistRequest(BaseModel):
    username: str


app = FastAPI(openapi_url=None)
app.mount(
    "/assets",
    StaticFiles(directory="assets"),
    name="assets",
)

templates = Jinja2Templates(directory="templates")

with open("config.json", "r") as f:
    config = json.load(f)
    turnstile_secret_key = config["turnstile_secret_key"]
    keycloak_server_url = config["keycloak_server_url"]
    keycloak_client_id = config["keycloak_client_id"]
    keycloak_client_secret_key = config["keycloak_client_secret_key"]
    keycloak_realm_name = config["keycloak_realm_name"]
    open_registration = config["open_registration"]

keycloak_connection = KeycloakOpenIDConnection(
    server_url=keycloak_server_url,
    realm_name=keycloak_realm_name,
    client_id=keycloak_client_id,
    client_secret_key=keycloak_client_secret_key,
    verify=True,
)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/update-password", response_class=HTMLResponse)
async def update_password(request: Request):
    return templates.TemplateResponse("password-update.html", {"request": request})


@app.post("/checkemailexist")
async def checkemailexist(request: Request, request_body: checkemailexistRequest):
    request_body = request_body.model_dump()
    if request_body["email"] in reserved_emails:
        return JSONResponse(content={"exist": True}, status_code=200)
    if dbmanager.get_user_by_email(request_body["email"]):
        return JSONResponse(content={"exist": True}, status_code=200)
    else:
        return JSONResponse(content={"exist": False}, status_code=200)


@app.post("/checkusernameexist")
async def checkusernameexist(request: Request, request_body: checkusernameexistRequest):
    request_body = request_body.model_dump()
    if request_body["username"] in reserved_users:
        return JSONResponse(content={"exist": True}, status_code=200)
    if dbmanager.get_user_by_name(request_body["username"]):
        return JSONResponse(content={"exist": True}, status_code=200)
    else:
        return JSONResponse(content={"exist": False}, status_code=200)


@app.post("/register", response_class=PlainTextResponse)
async def register(request: Request, request_body: Register_Request_Body):
    try:
        # check if open register
        if not open_registration:
            return "注册功能已关闭，请联系管理员。"

        request_body = request_body.model_dump()

        # verify captcha
        captcha_verify_response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": turnstile_secret_key,
                "response": request_body["token"],
                "remoteip": request.client.host,
            },
        )
        captcha_verify_response_json = captcha_verify_response.json()
        if not captcha_verify_response_json["success"]:
            return "验证码校验出错，请刷新网页重试，如果问题依旧，请联系管理员。"

        # validate email
        try:
            email = request_body["email"]
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError as e:
            return "邮件地址出错: " + str(e)

        # check if email is reserved
        if email in reserved_emails:
            return "该邮件地址为保留地址，请更换。"

        # check if email exists
        if dbmanager.get_user_by_email(email):
            return "邮件地址已被注册。"

        # check if username is reserved
        if request_body["username"] in reserved_users:
            return "该用户名为保留用户名，请更换。"

        # check if username exists
        if dbmanager.get_user_by_name(request_body["username"]):
            return "用户名已被注册。"

        # create user in keycloak
        try:
            keycloak_admin.create_user(
                {
                    "email": email,
                    "username": request_body["username"],
                    "emailVerified": True,
                    "enabled": True,
                    "credentials": [
                        {
                            "type": "password",
                            "value": request_body["password"],
                            "temporary": False,
                        }
                    ],
                    "attributes": {
                        "quota": "10G",
                    },
                    "groups": [
                        "网服队员",
                    ],
                }
            )
        except KeycloakGetError:
            return "用户名已被注册，请更改。"

        # use subprocess create user in docker-mailserver
        try:
            # docker exec -it dms setup email add <EMAIL ADDRESS> [<PASSWORD>]
            subprocess.run(
                [
                    "docker",
                    "exec",
                    "-it",
                    "dms",
                    "setup",
                    "email",
                    "add",
                    email,
                    shellquote(request_body["password"]),
                ],
            )
        except Exception as e:
            logger.error(e)
            return "出错了，请刷新网页重试，如果问题依旧，请联系管理员。"

    except Exception as e:
        logger.error(e)
        return "出错了，请刷新网页重试，如果问题依旧，请联系管理员。"

    dbmanager.add_user(request_body["username"], email)
    return "注册成功。"


@app.post("/passwordreset", response_class=PlainTextResponse)
async def passwordreset(request: Request, request_body: Password_Reset_Request_Body):
    try:
        request_body = request_body.model_dump()

        # verify captcha
        captcha_verify_response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": turnstile_secret_key,
                "response": request_body["token"],
                "remoteip": request.client.host,
            },
        )
        captcha_verify_response_json = captcha_verify_response.json()
        if not captcha_verify_response_json["success"]:
            return "验证码校验出错，请刷新网页重试，如果问题依旧，请联系管理员。"

        # validate email
        try:
            email = request_body["email"]
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError as e:
            return "邮件地址出错: " + str(e)

        # check if email exists
        if not dbmanager.get_user_by_email(email):
            return "邮件地址不存在。"

        # validate authcode
        authcode = request_body["authcode"]
        real_authcode = dbmanager.get_user_seed_by_email(email)
        if authcode != real_authcode:
            return "校验码错误，请仔细核对或联系管理员"

        # update user in keycloak
        try:
            # get username by email
            username = dbmanager.get_user_by_email(email)
            # get user_id by username
            user_id = keycloak_admin.get_user_id(username)
            keycloak_admin.set_user_password(
                user_id=user_id,
                password=request_body["password"],
                temporary=False,
            )

        except KeycloakGetError as e:
            logger.error(e)
            return "Keycloak密码更新失败，请联系管理员"

        # use subprocess to update user password in docker-mailserver
        try:
            # docker exec -it dms setup email add <EMAIL ADDRESS> [<PASSWORD>]
            subprocess.run(
                [
                    "docker",
                    "exec",
                    "-it",
                    "dms",
                    "setup",
                    "email",
                    "update",
                    email,
                    shellquote(request_body["password"]),
                ],
            )
        except Exception as e:
            logger.error(e)
            return "出错了，请刷新网页重试"

        # generate new authcode
        dbmanager.update_user_seed_by_email(email)

        return "密码修改成功"
    except Exception as e:
        logger.error(e)
        return "出错了，请刷新网页重试"
