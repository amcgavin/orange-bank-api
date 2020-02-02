import base64
import io
import subprocess

import requests
from PIL import Image, ImageOps
from utils import get_url

pinpad_url = "/KeypadService/v1/KeypadService.svc/json/PinpadImages"


def process_image(encoded: str) -> str:
    raw = io.BytesIO(base64.b64decode(encoded.encode("utf-8")))
    image = Image.open(raw)
    width, height = image.size
    image = image.crop((width / 4, height / 4, width - width / 4, height - height / 4)).convert(
        "RGB"
    )
    image = ImageOps.grayscale(ImageOps.invert(image))
    output = io.BytesIO()
    image.save(output, format="png", dpi=(70, 70))
    proc: subprocess.Popen = subprocess.Popen(
        args=["tesseract", "-", "-", "--psm", "10"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    stdout, _ = proc.communicate(output.getvalue())
    return stdout.decode("utf-8")[0]


def download_keypad():
    response = requests.get(get_url(pinpad_url))
    response.raise_for_status()
    data = response.json()
    keypad = [process_image(image) for image in data["KeypadImages"]]
    return keypad, data["Secret"], data["PemEncryptionKey"]
