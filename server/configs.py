import json

allow_email_hostnames = ["csuwf.com"]

# 5mins
captcha_session_timeout = 300

with open("config.json", "r", encoding="utf-8") as f:
    configs = json.load(f)
    keycloak_server_url = configs["keycloak_server_url"]
    keycloak_client_id = configs["keycloak_client_id"]
    keycloak_client_secret_key = configs["keycloak_client_secret_key"]
    keycloak_realm_name = configs["keycloak_realm_name"]
