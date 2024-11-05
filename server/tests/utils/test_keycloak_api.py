from utils.keycloak_api import (
    check_username_exist,
    check_email_exist,
    create_user,
    delete_user_by_id,
    delete_user_by_username,
    get_user_id,
)
from keycloak import KeycloakDeleteError
from utils.random_text import get_random_text


def test_check_username_exist():
    assert check_username_exist("bobmaster")
    assert not check_username_exist("somethingnotexist")


def test_check_email_exist():
    assert not check_email_exist("somethingnotexist@example.com")


def test_get_user_id():
    assert get_user_id("bobmaster")
    assert not get_user_id("somethingnotexist")


def test_create_delete_user_by_username():
    _username = get_random_text(8)
    _id = create_user(
        username=_username,
        password=get_random_text(16),
        email=f"{get_random_text(12)}@example.com",
    )
    assert _id
    assert type(delete_user_by_username(_username)) is dict


def test_delete_user():
    try:
        delete_user_by_id("cdaa7104-ac15-43eb-a8d3-c8986da441c6")
    except Exception as e:
        assert isinstance(e, KeycloakDeleteError)


if __name__ == "__main__":
    test_create_delete_user_by_username()
