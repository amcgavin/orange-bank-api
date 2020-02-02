import json
import os
import typing as t
from urllib.parse import urljoin

from Cryptodome.Hash import SHA1
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from requests import Response, request


def get_url(path: str) -> str:
    return urljoin(os.environ.get("BASE_URL", ""), path)


user_agent = "orange-bank-api; python/requests; version 1.0.0"


def _sign_message(token: str, body: str) -> t.Tuple[str, str]:
    key = RSA.generate(1024, e=int("10001", 16))
    signer = PKCS1_v1_5.new(key)
    digest = SHA1.new()
    digest.update(f"X-AuthToken:{token}{body}".encode("utf-8"))
    signature = signer.sign(digest)
    return signature.hex(), f"{key.n:x}"


def signed_request(
    method: str,
    url: str,
    token: str = "",
    body: t.Optional[dict] = None,
    headers: t.Optional[t.Mapping[str, str]] = None,
) -> Response:
    request_headers = {"User-Agent": user_agent, "Accept": "application/json"}
    if headers is not None:
        request_headers.update(headers)
    if body is not None:
        body = json.dumps(body)
        signature, sign_key = _sign_message(token, body)
        request_headers.update(
            {
                "x-authtoken": token,
                "x-messagesignature": signature,
                "x-messagesignkey": sign_key,
                "Content-Type": "application/json",
            }
        )
    return request(method, url, headers=request_headers, data=body)
