from configs import (
    keycloak_client_id,
    keycloak_client_secret_key,
    keycloak_realm_name,
    keycloak_server_url,
)
from keycloak import KeycloakAdmin, KeycloakGetError
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


def create_user(username: str, password: str, email: str) -> None:
    try:
        keycloak_admin.create_user(
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
    except KeycloakGetError as e:
        raise Exception(e)
