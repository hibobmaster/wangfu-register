from utils.keycloak_api import check_username_exist, check_email_exist


def test_check_username_exist():
    assert check_username_exist("bobmaster")
    assert not check_username_exist("somethingnotexist")


def test_check_email_exist():
    assert check_email_exist("bobmaster@csuwf.com")
    assert not check_email_exist("somethingnotexist@example.com")
