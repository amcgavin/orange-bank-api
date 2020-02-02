import base64
import io
import subprocess

from PIL import Image, ImageOps
from utils import get_url, signed_request

pinpad_url = "/KeypadService/v1/KeypadService.svc/json/PinpadImages"


def process_image(encoded: str) -> str:
    raw = io.BytesIO(base64.b64decode(encoded.encode("utf-8")))
    image = Image.open(raw)
    width, height = image.size

    # need to crop the image down to get rid of the rounded corners
    image = image.crop((width / 4, height / 4, width - width / 4, height - height / 4)).convert(
        "RGB"
    )

    # Image should be inverted so the text colour is black.
    # greyscale also improves the readability
    image = ImageOps.grayscale(ImageOps.invert(image))
    output = io.BytesIO()
    image.save(output, format="png", dpi=(70, 70))

    proc: subprocess.Popen = subprocess.Popen(
        args=["tesseract", "-", "-", "--psm", "10"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    stdout, _ = proc.communicate(output.getvalue())
    return stdout.decode("utf-8")[0]


def download_keypad():
    response = signed_request("GET", get_url(pinpad_url))
    response.raise_for_status()
    data = response.json()
    keypad = [process_image(image) for image in data["KeypadImages"]]
    return keypad, data["Secret"], data["PemEncryptionKey"]
