import json
import os
import glob

# 포트홀만 추출 (category_id 8번)
POTHOLE_CATEGORY_ID = 8

def convert_bbox_to_yolo(bbox, img_width, img_height):
    x, y, w, h = bbox
    x_center = (x + w / 2) / img_width
    y_center = (y + h / 2) / img_height
    w_norm = w / img_width
    h_norm = h / img_height
    return x_center, y_center, w_norm, h_norm

def convert_json_to_yolo(json_path, output_dir):
    with open(json_path, 'r') as f:
        data = json.load(f)

    img_width = data['images']['width']
    img_height = data['images']['height']
    img_filename = data['images']['file_name']

    pothole_annotations = [
        ann for ann in data['annotations']
        if ann['category_id'] == POTHOLE_CATEGORY_ID
    ]

    if not pothole_annotations:
        return False

    base_name = os.path.splitext(img_filename)[0]
    txt_path = os.path.join(output_dir, base_name + '.txt')

    with open(txt_path, 'w') as f:
        for ann in pothole_annotations:
            x_c, y_c, w, h = convert_bbox_to_yolo(
                ann['bbox'], img_width, img_height
            )
            f.write(f"0 {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")

    return True

def main():
    json_dir = "data/raw"
    output_dir = "data/labels"
    os.makedirs(output_dir, exist_ok=True)

    json_files = glob.glob(
        os.path.join(json_dir, "**/*.json"), recursive=True
    )

    total = 0
    converted = 0

    for json_path in json_files:
        total += 1
        if convert_json_to_yolo(json_path, output_dir):
            converted += 1

    print(f"전체 JSON: {total}개")
    print(f"포트홀 포함: {converted}개")
    print(f"변환 완료 → data/labels/")

if __name__ == "__main__":
    main()
