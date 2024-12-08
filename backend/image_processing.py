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
        np.ones((insert_height, insert_width), dtype=np.uint8) * 255,
        M,
        (base_img.shape[1], base_img.shape[0])
    )

    if len(base_img.shape) == 3 and base_img.shape[2] == 3:
        mask = cv2.merge([mask, mask, mask])
    mask_inv = cv2.bitwise_not(mask)
    if warped_img.dtype != base_img.dtype:
        warped_img = warped_img.astype(base_img.dtype)

    base_background = cv2.bitwise_and(base_img, mask_inv)
    final_result = cv2.add(base_background, warped_img)

    return final_result

def crop_text_regions(selected_objects, results_dir):
    os.makedirs(results_dir, exist_ok=True)

    for obj in selected_objects:
        cropped_image_path = obj["cropped_image_path"].replace(f"/static/", "./static/")
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

            if os.path.exists(save_path):
                print(f"Cropped image saved at {save_path}")
                region["text_image_path"] = f"/static/text_regions/{obj['id']}_region_{region_id}.png"
                print(f"Updated region: {region}")
            else:
                print(f"Failed to save cropped image at {save_path}")
    return selected_objects

def merge_text_regions(obj):
    cropped_image_path = obj['cropped_image_path'].replace("/static/", "./static/")
    cropped_img = cv2.imread(cropped_image_path)

    if cropped_img is None:
        print(f"Error: Cannot load cropped image at {cropped_image_path}")
        return False

    for region in obj['text_regions']:
        text_image_path = region['text_image_path'].replace("/static/", "./static/")
        text_img = cv2.imread(text_image_path)

        if text_img is None:
            print(f"Error: Cannot load text image at {text_image_path}")
            continue

        region_h, region_w = text_img.shape[:2]
        polygon = np.array(region['polygon'], dtype=np.float32)

        if polygon.size == 0:
            print(f"Error: Empty polygon for region {region['region_id']}")
            continue

        try:
            text_coords = np.array([[0, 0], [region_w, 0], [region_w, region_h], [0, region_h]], dtype=np.float32)
            M = cv2.getPerspectiveTransform(text_coords, polygon)
        except cv2.error as e:
            print(f"Error: Failed to compute perspective transform for region {region['region_id']}: {e}")
            continue

        warped_text_img = cv2.warpPerspective(text_img, M, (cropped_img.shape[1], cropped_img.shape[0]))

        mask = np.zeros((cropped_img.shape[0], cropped_img.shape[1]), dtype=np.uint8)
        cv2.fillPoly(mask, [polygon.astype(np.int32)], 255)

        mask_inv = cv2.bitwise_not(mask)
        cropped_background = cv2.bitwise_and(cropped_img, cropped_img, mask=mask_inv)

        warped_text_img = cv2.bitwise_and(warped_text_img, warped_text_img, mask=mask)
        cropped_img = cv2.add(cropped_background, warped_text_img)

    cv2.imwrite(cropped_image_path, cropped_img)
    print(f"Updated cropped image saved at {cropped_image_path}")
    return True
