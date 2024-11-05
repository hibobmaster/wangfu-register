import random
import string


def get_random_text(length: int = 4) -> str:
    return "".join(
        (random.choice(string.ascii_letters + string.digits) for _ in range(length))
    )
