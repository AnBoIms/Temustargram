import easyocr
import cv2
import numpy as np
import re

reader = easyocr.Reader(['ko', 'en'])

def ocr_result(image_path):
    result = reader.readtext(image_path)
    return result

# 같은 카테고리 내 바운딩 박스 병합
def merge_boxes(boxes):
    if not boxes:
        return []

    result = []
    x_min = min([box[0][0][0] for box in boxes])
    y_min = min([box[0][0][1] for box in boxes])
    x_max = max([box[0][2][0] for box in boxes])
    y_max = max([box[0][2][1] for box in boxes])

    all_text = " ".join([box[1] for box in boxes])
    result.append(([[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]], all_text))

    return result

# OCR 결과 처리 및 카테고리 별 분류
def process_ocr_results(ocr_results):
    resident_id_top_y = None
    address_start_y = None
    first_resident_id_box = None
    name_box = None
    resident_id_boxes = []
    address_boxes = []
    excluded_boxes = []

    ocr_results = sorted(ocr_results, key=lambda x: x[0][0][1])
    closest_distance = float('inf')
    
    # 주민등록증 텍스트 찾기 (가장 위쪽 텍스트)
    if ocr_results:
        first_box = ocr_results[0]
        coords, text, confidence = first_box
        resident_id_top_y = (coords[0][1] + coords[2][1]) / 2

    
    # 이름, 주민등록번호, 주소 분류
    for box in ocr_results:
        coords, text, confidence = box
        text_cleaned = re.sub(r'\s+', '', text)

        # '주민등록증' 텍스트 위 텍스트는 제외
        if resident_id_top_y and coords[0][1] <= resident_id_top_y:
            excluded_boxes.append(box)
            continue

        # 이름 추출
        if resident_id_top_y and coords[0][1] > resident_id_top_y :
            distance = coords[0][1] - resident_id_top_y
            if distance < closest_distance:
                name_box = (coords, text_cleaned)
                closest_distance = distance
                continue
        
        # 주민등록번호 추출
        if re.match(r'^[0-9A-Za-z가-힣\-.,!?@#$%^&*()_+=]+$', text_cleaned):
            if not first_resident_id_box:
                first_resident_id_box = box
                resident_id_boxes.append(box)
                address_start_y = (coords[0][1] + coords[2][1]) / 2
                continue
            else:
                first_box_top_y = first_resident_id_box[0][0][1]
                current_box_top_y = coords[0][1]
                if abs(current_box_top_y - first_box_top_y) > 10:
                    pass  
                else:
                    resident_id_boxes.append(box)  
                    continue
        
        # 발급 날짜 및 구청장 텍스트 분류
        if re.match(r'^[0-9\s.*]+$', text_cleaned) or "구청장" in text_cleaned or "시장" in text_cleaned:
            excluded_boxes.append(box)
            continue

        # 주소 추출 (주민등록번호 아래 텍스트)
        if address_start_y and coords[0][1]  > address_start_y :
            address_boxes.append(box)
            continue

        if name_box and box[0] == name_box[0]:
            continue
        
        # 제외 대상
        excluded_boxes.append(box)

    merged_resident_id = merge_boxes(resident_id_boxes)

    merged_address = merge_boxes(address_boxes)

    return {
        "name": [name_box] if name_box else [],
        "resident_id": merged_resident_id,
        "address": merged_address
    }

def process_bounding_box(image, texture_path, bounding_box):
    texture = cv2.imread(texture_path, cv2.IMREAD_UNCHANGED)
    h, w, _ = texture.shape

    bounding_box = np.array(bounding_box, dtype=np.float32)

    texture_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)

    M = cv2.getPerspectiveTransform(texture_points, bounding_box)

    warped_texture = cv2.warpPerspective(texture, M, (image.shape[1], image.shape[0]))

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.int32(bounding_box)], 255)

    inpainted_image = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    if warped_texture.shape[2] == 4: 
        alpha_channel = warped_texture[:, :, 3]
        bgr_texture = warped_texture[:, :, :3]
    else:
        alpha_channel = np.ones_like(warped_texture[:, :, 0]) * 255
        bgr_texture = warped_texture

    alpha_channel = alpha_channel / 255.0  
    for c in range(0, 3):
        inpainted_image[:, :, c] = (
            inpainted_image[:, :, c] * (1 - alpha_channel) +
            bgr_texture[:, :, c] * alpha_channel
        )

    return inpainted_image

def apply_blur(image_path, output_path, blur_intensity=45):
    blurred_image = cv2.GaussianBlur(image_path, (blur_intensity, blur_intensity), 0)

    cv2.imwrite(output_path, blurred_image)