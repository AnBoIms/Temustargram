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
