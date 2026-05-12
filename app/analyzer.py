import io
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from ultralytics import YOLO

MODEL_PATH = Path(__file__).resolve().parent.parent / "best.pt"
MAX_ANALYSIS_DIMENSION = 1280
INFERENCE_IMAGE_SIZE = 640
CONFIDENCE_THRESHOLD = 0.3


@lru_cache(maxsize=1)
def get_model() -> YOLO:
    return YOLO(str(MODEL_PATH))


def load_image(image_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    img.load()
    return img.convert("RGB")


def resize_for_analysis(img: Image.Image) -> Image.Image:
    if max(img.size) <= MAX_ANALYSIS_DIMENSION:
        return img

    resized = img.copy()
    resized.thumbnail((MAX_ANALYSIS_DIMENSION, MAX_ANALYSIS_DIMENSION), Image.Resampling.LANCZOS)
    return resized


def check_image_quality(img: Image.Image) -> tuple[bool, str]:
    brightness = np.asarray(img.convert("L")).mean()

    if brightness < 50:
        return False, "조명이 부족합니다. 밝은 곳에서 촬영해주세요"
    if brightness > 220:
        return False, "역광입니다. 햇빛을 등지고 촬영해주세요"
    return True, "ok"


def analyze_image(image_bytes: bytes) -> dict:
    original_img = load_image(image_bytes)
    img = resize_for_analysis(original_img)
    ok, message = check_image_quality(img)
    if not ok:
        return {
            "detected": False,
            "confidence": 0.0,
            "area_ratio": 0.0,
            "damage_score": 0.0,
            "bbox": None,
            "message": message
        }

    results = get_model().predict(
        img,
        imgsz=INFERENCE_IMAGE_SIZE,
        conf=CONFIDENCE_THRESHOLD,
        verbose=False,
    )

    detected = False
    confidence = 0.0
    area_ratio = 0.0
    damage_score = 0.0
    bbox = None

    img_area = img.width * img.height
    scale_x = original_img.width / img.width
    scale_y = original_img.height / img.height

    for result in results:
        for box in result.boxes:
            conf = float(box.conf[0])
            if conf < CONFIDENCE_THRESHOLD:
                continue
            detected = True
            confidence = conf
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            box_area = (x2 - x1) * (y2 - y1)
            area_ratio = box_area / img_area
            damage_score = min(confidence * area_ratio * 1000, 100)
            bbox = [x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y]
            break

    return {
        "detected": detected,
        "confidence": round(confidence, 4),
        "area_ratio": round(area_ratio, 4),
        "damage_score": round(damage_score, 2),
        "bbox": bbox,
        "message": "포트홀 감지됨" if detected else "포트홀 미감지"
    }
