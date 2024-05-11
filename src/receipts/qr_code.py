# https://vc.ru/newtechaudit/301060-computer-vision-v-pomoshch-dekodirovaniya-qr-koda-na-python
import os.path
import re

import cv2
from pyzbar import pyzbar


class QRCReader:
    def __init__(self, filename: str):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"No such file or directory: {filename!r}")
        self.filename = filename
        self.qrcodes: list[str] = []

    def read(self):
        img = cv2.imread(self.filename)
        all_data = pyzbar.decode(img)
        for data in all_data:
            if data.type == 'QRCODE':
                self.qrcodes.append(data.data.decode('utf-8'))

    def all(self):
        return self.read()

    def filter(self, re_str: str) -> list[str]:
        self.read()
        re_filter = re.compile(re_str)
        return [qr for qr in self.qrcodes if re_filter.fullmatch(qr)]
