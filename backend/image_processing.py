import numpy as np
import cv2
import os

def distance(pt1, pt2):
    return np.linalg.norm(np.array(pt1) - np.array(pt2))

def crop_and_transform_object(img, obj, results_dir):
    polygon = np.array(obj["polygon"], dtype=np.float32)
    id_type = obj["type"]

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
        save_path = os.path.join(results_dir, f'{obj["id"]}_{id_type}.png')
        cv2.imwrite(save_path, cropped_img)
        return save_path

    M = cv2.getPerspectiveTransform(ordered_polygon, pts2)
    transformed_img = cv2.warpPerspective(img, M, (output_width, output_height))

    save_path = os.path.join(results_dir, f'{obj["id"]}_{id_type}.png')
    cv2.imwrite(save_path, transformed_img)
    return save_path

def crop_text_regions(selected_objects, results_dir, server_host):
    os.makedirs(results_dir, exist_ok=True)

    for obj in selected_objects:
        cropped_image_path = obj["cropped_image_path"] 
        cropped_image = cv2.imread(cropped_image_path.replace(server_host, ".")) 

        if cropped_image is None:
            print(f"Error: Cannot load cropped image at {cropped_image_path}")
            continue

        for region in obj["text_regions"]:
            polygon = np.array(region["polygon"], dtype=np.float32)

            x, y, w, h = cv2.boundingRect(polygon)
            cropped_region = cropped_image[int(y):int(y+h), int(x):int(x+w)] 

            region_id = region["region_id"]
            save_path = os.path.join(results_dir, f'{obj["id"]}_region_{region_id}.png')
            cv2.imwrite(save_path, cropped_region)

            region["cropped_image_path"] = f"{server_host}/static/text_regions/{obj['id']}_region_{region_id}.png"