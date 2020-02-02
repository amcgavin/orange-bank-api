import base64

from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from utils import get_url, signed_request

from .keypad import download_keypad

login_url = "/STSServiceB2C/V1/SecurityTokenServiceProxy.svc/issue"


def encrypt_pin(pin: str, key: str) -> str:
    rsa_key = RSA.import_key(key)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted = base64.b64encode(cipher.encrypt(pin.encode("utf-8"))).decode("utf-8")
    return encrypted


def login(account_number: str, pin: str):
    keypad, secret, key = download_keypad()
    translated_pin = ",".join(str(keypad.index(x)) for x in pin)
    auth_pin = encrypt_pin(translated_pin, key)
    return signed_request(
        "POST",
        get_url(login_url),
        token="",
        body={},
        headers={"x-authcif": account_number, "x-authpin": auth_pin, "x-authsecret": secret},
    )
