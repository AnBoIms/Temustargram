import numpy as np
import cv2
import os

def distance(pt1, pt2):
    return np.linalg.norm(np.array(pt1) - np.array(pt2))
    
def crop_and_transform_object(img, obj, results_dir):
    polygon = np.array(obj["polygon"], dtype=np.float32)
    id_type = obj["type"]

    type_dir = os.path.join(results_dir, id_type)
    os.makedirs(type_dir, exist_ok=True)

    polygon = sorted(polygon, key=lambda p: p[0])  
    left_group = sorted(polygon[:2], key=lambda p: p[1])  
    right_group = sorted(polygon[2:], key=lambda p: p[1])  

    top_left = left_group[0]
    bottom_left = left_group[1]
    top_right = right_group[0]
    bottom_right = right_group[1]

    ordered_polygon = np.float32([top_left, bottom_left, bottom_right, top_right])

    if id_type == "id_card":
        output_width, output_height = 860, 540
        pts2 = np.float32([[0, 0], [0, output_height], [output_width, output_height], [output_width, 0]])

    elif id_type == "sign":
        width_top = distance(top_left, top_right)
        width_bottom = distance(bottom_left, bottom_right)
        output_width = int(max(width_top, width_bottom))
        height_left = distance(top_left, bottom_left)
        height_right = distance(top_right, bottom_right)
        output_height = int(max(height_left, height_right))
        pts2 = np.float32([[0, 0], [0, output_height], [output_width, output_height], [output_width, 0]])

    else:
        x, y, w, h = cv2.boundingRect(polygon)
        cropped_img = img[y:y+h, x:x+w]
        save_path = os.path.join(type_dir, f'{obj["id"]}_{id_type}.png')
        cv2.imwrite(save_path, cropped_img)
        return save_path

    M = cv2.getPerspectiveTransform(ordered_polygon, pts2)
    transformed_img = cv2.warpPerspective(img, M, (output_width, output_height))
    save_path = os.path.join(type_dir, f'{obj["id"]}_{id_type}.png')
    cv2.imwrite(save_path, transformed_img)
    return save_path, ordered_polygon

def insert_image_final(base_img, insert_img, polygon):
    polygon = np.float32(polygon)

    insert_height, insert_width = insert_img.shape[:2]
    insert_coords = np.float32([[0, 0], [0, insert_height], [insert_width, insert_height], [insert_width, 0]])

    M = cv2.getPerspectiveTransform(insert_coords, polygon)
    warped_img = cv2.warpPerspective(insert_img, M, (base_img.shape[1], base_img.shape[0]))

    mask = cv2.warpPerspective(
        np.ones((insert_height, insert_width), dtype=np.uint8) * 255,  # 단일 채널
        M,
        (base_img.shape[1], base_img.shape[0])
    )

    if len(base_img.shape) == 3 and base_img.shape[2] == 3:  # base_img가 BGR 이미지일 경우
        mask = cv2.merge([mask, mask, mask])
    mask_inv = cv2.bitwise_not(mask)
    if warped_img.dtype != base_img.dtype:
        warped_img = warped_img.astype(base_img.dtype)

    base_background = cv2.bitwise_and(base_img, mask_inv)
    final_result = cv2.add(base_background, warped_img)

    return final_result

def crop_text_regions(selected_objects, results_dir, server_host):
    # 디렉토리 생성
    os.makedirs(results_dir, exist_ok=True)

    for obj in selected_objects:
        # cropped_image_path를 로컬 경로로 변환
        cropped_image_path = obj["cropped_image_path"].replace(f"{server_host}/static/", "./static/")

        # 이미지 경로 검증
        if not os.path.exists(cropped_image_path):
            print(f"Error: File not found at {cropped_image_path}")
            continue

        cropped_image = cv2.imread(cropped_image_path)
        if cropped_image is None:
            print(f"Error: Cannot load image at {cropped_image_path}")
            continue

        if not obj.get("text_regions"):
            print(f"No text regions found for object ID {obj['id']}")
            continue

        for region in obj["text_regions"]:
            polygon = np.array(region["polygon"], dtype=np.float32)
            if len(polygon) == 0:
                print(f"Empty polygon for region in object ID {obj['id']}")
                continue

            x, y, w, h = cv2.boundingRect(polygon)

            # 이미지 크기를 초과하지 않도록 좌표 보정
            height, width = cropped_image.shape[:2]
            x_end, y_end = min(x + w, width), min(y + h, height)
            x, y = max(x, 0), max(y, 0)
            cropped_region = cropped_image[y:y_end, x:x_end]

            if cropped_region.size == 0:
                print(f"Empty cropped region for object ID {obj['id']} region ID {region.get('region_id', 'unknown')}")
                continue

            region_id = region.get("region_id", "unknown")
            save_path = os.path.join(results_dir, f'{obj["id"]}_region_{region_id}.png')
            cv2.imwrite(save_path, cropped_region)

            # 저장 확인 및 경로 추가
            if os.path.exists(save_path):
                print(f"Cropped image saved at {save_path}")
                region["cropped_image_path"] = f"{server_host}/static/text_regions/{obj['id']}_region_{region_id}.png"
            else:
                print(f"Failed to save cropped image at {save_path}")

def merge_text_regions_with_cropped(cropped_image_path, text_regions):
    # 원본 잘린 이미지를 로드
    cropped_image = cv2.imread(cropped_image_path)
    if cropped_image is None:
        print(f"Error: Cannot load cropped image at {cropped_image_path}")
        return False

    for region in text_regions:
        # 텍스트 영역 이미지 로드
        text_image_path = region.get("cropped_image_path")
        if not text_image_path or not os.path.exists(text_image_path):
            print(f"Error: Cannot load text region image at {text_image_path}")
            continue

        text_image = cv2.imread(text_image_path, cv2.IMREAD_UNCHANGED)
        if text_image is None:
            print(f"Error: Cannot load text image at {text_image_path}")
            continue

        # 텍스트 영역 polygon 가져오기
        polygon = np.array(region.get("polygon"), dtype=np.float32)
        if len(polygon) == 0:
            print(f"Empty polygon for text region in cropped image {cropped_image_path}")
            continue

        # 텍스트 이미지의 크기 계산
        text_height, text_width = text_image.shape[:2]
        text_coords = np.array([[0, 0], [0, text_height], [text_width, text_height], [text_width, 0]], dtype=np.float32)

        # 투영 변환 매트릭스 계산 및 텍스트 이미지 변환
        M = cv2.getPerspectiveTransform(text_coords, polygon)
        warped_text_image = cv2.warpPerspective(text_image, M, (cropped_image.shape[1], cropped_image.shape[0]))

        # 마스크 생성 (투명한 배경 포함)
        mask = cv2.warpPerspective(np.ones_like(text_image, dtype=np.uint8) * 255, M, (cropped_image.shape[1], cropped_image.shape[0]))
        mask_inv = cv2.bitwise_not(mask)

        # 합성 과정
        cropped_bg = cv2.bitwise_and(cropped_image, mask_inv)
        final_result = cv2.add(cropped_bg, warped_text_image)

        # 업데이트된 이미지를 원본에 적용
        cropped_image = final_result

    # 최종 이미지를 덮어쓰기
    cv2.imwrite(cropped_image_path, cropped_image)
    print(f"Updated cropped image saved at {cropped_image_path}")
    return True