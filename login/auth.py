import base64
import typing as t

import requests
from Cryptodome.Cipher import PKCS1_v1_5 as Cipher
from Cryptodome.Hash import SHA1
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5 as Signer
from utils import get_url

from .keypad import download_keypad

login_url = "/STSServiceB2C/V1/SecurityTokenServiceProxy.svc/issue"


def encrypt_pin(pin: str, key: str) -> str:
    rsa_key = RSA.import_key(key)
    cipher = Cipher.new(rsa_key)
    encrypted = base64.b64encode(cipher.encrypt(pin.encode("utf-8"))).decode("utf-8")
    return encrypted


def sign_message(token: str, body: str) -> t.Tuple[str, str]:
    key = RSA.generate(1024, e=int("10001", 16))
    signer = Signer.new(key)
    digest = SHA1.new()
    digest.update(f"X-AuthToken:{token}{body}".encode("utf-8"))
    signature = signer.sign(digest)
    return signature.hex(), f"{key.n:x}"


def login(account_number: str, pin: str):
    keypad, secret, key = download_keypad()
    translated_pin = ",".join(str(keypad.index(x)) for x in pin)
    auth_pin = encrypt_pin(translated_pin, key)
    signature, modulus = sign_message("", {})
    return requests.post(
        get_url(login_url),
        headers={
            "x-authcif": account_number,
            "x-authpin": auth_pin,
            "x-authsecret": secret,
            "x-authtoken": "",
            "x-messagesignature": signature,
            "x-messagesignkey": modulus,
        },
        json={},
        allow_redirects=False,
    )
