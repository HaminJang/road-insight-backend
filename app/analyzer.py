import numpy as np
from PIL import Image
import io
from ultralytics import YOLO

model = YOLO("best.pt")

def check_image_quality(image_bytes: bytes) -> tuple[bool, str]:
    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    brightness = np.array(img).mean()

    if brightness < 50:
        return False, "조명이 부족합니다. 밝은 곳에서 촬영해주세요"
    if brightness > 220:
        return False, "역광입니다. 햇빛을 등지고 촬영해주세요"
    return True, "ok"

def analyze_image(image_bytes: bytes) -> dict:
    ok, message = check_image_quality(image_bytes)
    if not ok:
        return {
            "detected": False,
            "confidence": 0.0,
            "area_ratio": 0.0,
            "damage_score": 0.0,
            "bbox": None,
            "message": message
        }

    img = Image.open(io.BytesIO(image_bytes))
    results = model(img)

    detected = False
    confidence = 0.0
    area_ratio = 0.0
    damage_score = 0.0
    bbox = None

    img_area = img.width * img.height

    for result in results:
        for box in result.boxes:
            conf = float(box.conf[0])
            if conf < 0.3:
                continue
            detected = True
            confidence = conf
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            box_area = (x2 - x1) * (y2 - y1)
            area_ratio = box_area / img_area
            damage_score = min(confidence * area_ratio * 1000, 100)
            bbox = [x1, y1, x2, y2]
            break

    return {
        "detected": detected,
        "confidence": round(confidence, 4),
        "area_ratio": round(area_ratio, 4),
        "damage_score": round(damage_score, 2),
        "bbox": bbox,
        "message": "포트홀 감지됨" if detected else "포트홀 미감지"
    }
