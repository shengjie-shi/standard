# -*- coding: utf-8 -*-
"""
Description:

@Author: ssjie

Created on: 2026/5/7
"""
import re
import numpy as np
import base64
import cv2


def limit_imgsz(img, min_size=640, max_size=960):
    if min_size > max_size:
        min_size = max_size

    im_size_max = np.max(img.shape[:2])
    if min_size <= im_size_max <= max_size:
        return img, 1
    input_size = min_size if im_size_max < min_size else max_size
    im_scale = float(input_size) / float(im_size_max)
    img = cv2.resize(img, None, None, fx=im_scale, fy=im_scale)
    return img, im_scale


def read_img_cn(img_path):
    return cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)


def save_img_cn(img_path, img, ext=".jpg"):
    cv2.imencode(ext, img)[1].tofile(img_path)


def readimg_base64(img_path):
    with open(img_path, "rb") as fp:
        img_info = fp.read()
    img_base64 = base64.b64encode(img_info).decode("utf-8")
    return img_base64


def encode_nparrayimg(img_ndarray, ext=".jpg"):
    img_base64 = cv2.imencode(ext, img_ndarray)[1]
    img_base64 = base64.b64encode(img_base64).decode("utf-8")
    return img_base64


def decode_base64img(img_base64):
    img = bytes(img_base64.encode("utf-8"))
    img = base64.b64decode(img)
    img = cv2.imdecode(np.frombuffer(img, np.uint8), 1)
    return img


def is_base64code(string):

    if not isinstance(string, str):
        return False

    if string.startswith("data") and "," in string:
        _string = string.split(",", 1)[1]

    else:
        _string = string

    # 检查base64字符串格式
    base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
    if not base64_pattern.match(_string):
        return False
    try:
        # 尝试解码
        decoded = base64.b64decode(_string, validate=True)
        # 确保解码后不是空数据
        return len(decoded) > 0
    except ValueError:
        return False


if __name__ == "__main__":

    img_path = r"D:\Code\Project\PaddleOCR_2\data\images\certs\business_license\data_processed\test_data\test_imgs\00021.png"

    pdf_path = r"D:\Code\Project\PaddleOCR_2\PaddleOCR_VL\data\附件1：考勤管理制度.pdf"

    base64code = readimg_base64(img_path)

    print(is_base64code(base64code))

    img_ndarray = decode_base64img(base64code)

    print(isinstance(img_ndarray, np.ndarray))


