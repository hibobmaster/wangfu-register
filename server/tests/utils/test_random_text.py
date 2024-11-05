from utils.random_text import get_random_text


def test_get_random_text():
    assert len(get_random_text()) == 4
    assert len(get_random_text(10)) == 10
