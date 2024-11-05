from configs import (
    keycloak_client_id,
    keycloak_client_secret_key,
    keycloak_realm_name,
    keycloak_server_url,
)
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection


keycloak_connection = KeycloakOpenIDConnection(
    server_url=keycloak_server_url,
    realm_name=keycloak_realm_name,
    client_id=keycloak_client_id,
    client_secret_key=keycloak_client_secret_key,
    verify=True,
)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)


def check_username_exist(username: str) -> bool:
    user_id = keycloak_admin.get_user_id(username)
    return False if user_id is None else True


def check_email_exist(email: str) -> bool:
    results = keycloak_admin.get_users({"email": email})
    if len(results) == 0:
        return False
    else:
        return True


def get_user_id(username: str) -> str:
    return keycloak_admin.get_user_id(username)


def create_user(username: str, password: str, email: str) -> str | None:
    _id = keycloak_admin.create_user(
        {
            "email": email,
            "username": username,
            "emailVerified": True,
            "enabled": True,
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False,
                }
            ],
            "attributes": {
                "quota": "10G",
            },
            "groups": ["网服队员"],
        }
    )
    return _id


def delete_user_by_username(username: str) -> dict | None:
    _id = keycloak_admin.get_user_id(username)
    if not _id:
        return

    response = keycloak_admin.delete_user(_id)
    return response


def delete_user_by_id(id: str) -> dict | None:
    return keycloak_admin.delete_user(id)
