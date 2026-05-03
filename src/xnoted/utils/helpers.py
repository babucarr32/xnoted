import base64
import hashlib
from pathlib import Path
import time


def get_current_time_milli():
    return int(round(time.time() * 10000))


def debouncer(callback, throttle_time_limit=1000):
    last_millis = get_current_time_milli()

    def throttle():
        nonlocal last_millis
        curr_millis = get_current_time_milli()
        if (curr_millis - last_millis) > throttle_time_limit:
            last_millis = get_current_time_milli()
            callback()

    return throttle


def slugify(text: str):
    return text.lower().replace(" ", "_")


def mask(text: str = "", unmasked: int = 6) -> str:
    if not text:
        return "".join(["*" for x in range(10)])

    if len(text) <= unmasked:
        return text

    return "*" * (len(text) - unmasked) + text[-unmasked:]

def find_file(file_name: str) -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        f = parent / file_name
        if f.exists():
            return f
    raise FileNotFoundError(f"{file_name} not found")


def derive_encryption_key(password: str) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
