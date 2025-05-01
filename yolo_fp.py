# from roboflow import Roboflow
from ultralytics import YOLO
from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np
import re
from ppocr.utils.logging import get_logger
import logging
logger = get_logger()
logger.setLevel(logging.ERROR)
import cv2

dimension_pattern = re.compile(r"\b(\d+(?:\.\d+)?)[\s]*m?[\s]*[x×][\s]*(\d+(?:\.\d+)?)[\s]*m?\b", re.IGNORECASE)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Load image
image_path = "456.jpg"
image_plot = Image.open(image_path)
draw_plot = ImageDraw.Draw(image_plot)

model = YOLO("fp_50.pt")

try:
    font = ImageFont.truetype("arial.ttf", size=26)
except:
    font = ImageFont.load_default()

 
# result = model.predict("123.jpg", confidence=40, overlap=30).json()
result = model(image_path, conf=0.85)[0]


image = Image.open(image_path).convert("RGB")
draw = ImageDraw.Draw(image)
image_np = np.array(image)

structured_results = []

# Loop over each YOLO detection
for i, (obb, conf, cls_id) in enumerate(zip(result.obb.data, result.obb.conf, result.obb.cls)):
    cx, cy, w, h, angle = map(float, obb[:5])  # Convert to float

    # Convert OBB to 4-point polygon
    rect = ((cx, cy), (w, h), angle)
    box = cv2.boxPoints(rect)
    points = np.int0(box)

    # Create mask for polygon
    mask_img = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask_img).polygon([tuple(p) for p in points], outline=1, fill=1)
    mask_np = np.array(mask_img)

    masked_region = np.zeros_like(image_np)
    for c in range(3):
        masked_region[:, :, c] = image_np[:, :, c] * mask_np

    # Crop the bounding box of the polygon
    xs, ys = zip(*points)
    min_x, max_x = int(min(xs)), int(max(xs))
    min_y, max_y = int(min(ys)), int(max(ys))
    cropped = masked_region[min_y:max_y, min_x:max_x]

    # OCR
    room_info = {"room_id": i + 1, "type": None, "dimensions": None}
    ocr_result = ocr.ocr(cropped, cls=True)
    # print(f"\n--- OCR Result for Room {i+1} ---")
    if (ocr_result[0] != None):
        for line in ocr_result[0]:
            text = line[1][0]
            confidence = line[1][1]
            if (confidence > 0.5):
                # print(f"Text: {text}, Confidence: {confidence:.2f}")
                if dimension_pattern.search(text) and any(unit in text.lower() for unit in ["m", "ft", "'"]):
                    # print("Dimentions :",text)
                    room_info["dimensions"] = text
                elif not dimension_pattern.search(text) and (len(text)>= 4) and not text.isnumeric():
                    # print("Type :",text)
                    room_info["type"] = text
    structured_results.append(room_info)
    draw_plot.polygon([tuple(p) for p in points], outline="red", width=2)
    label_text = f"{room_info['type'] or 'room'} ({confidence:.2f})"
    draw_plot.text((min_x, min_y - 10), label_text, fill="red", font=font)


print(structured_results)
# Show the image with predictions
plt.figure(figsize=(10, 8))
plt.imshow(image_plot)
plt.axis("off")
plt.show()