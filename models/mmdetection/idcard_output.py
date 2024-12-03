from mmdet.apis import init_detector, inference_detector
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

# 1. 모델 설정
config_file = 'configs/anboims_dataset/mask-rcnn_r50-caffe_fpn_ms-poly-1x_anboimsdataset.py'
checkpoint_file = 'work_dirs/mask-rcnn_r50-caffe_fpn_ms-poly-1x_anboimsdataset/epoch_12.pth'
model = init_detector(config_file, checkpoint_file, device='cpu')

# 2. 입력 이미지 경로 설정
input_image_path = 'test_images/KakaoTalk_20241129_131248208.jpg'  # 테스트할 이미지
output_polygon_path = 'output/polygon_result.jpg'  # polygon 처리 결과 저장 경로
output_coords_path = 'output/convex_coords.txt'    # Convex Hull 좌표 저장 경로
output_orig_coords_path = 'output/original_coords.txt'  # 원본 좌표 저장 경로

# 3. Convex Hull 좌표 추출 함수
def get_coordinate(segmentation_points):
    points = np.array(segmentation_points, dtype=np.float32)
    hull = cv2.convexHull(points)
    rect = cv2.minAreaRect(hull)
    box = cv2.boxPoints(rect)
    return np.int0(box).tolist()

# 4. 모델 추론
result = inference_detector(model, input_image_path)
img = cv2.imread(input_image_path)

# 5. 결과 처리
masks = result.pred_instances.masks.cpu().numpy()
convex_coordinates_list = []
original_coordinates_list = []
polygon_img = img.copy()

for mask in masks:
    if mask.sum() > 0:
        # 원본 segmentation 좌표 추출
        segmentation_points = np.argwhere(mask > 0)
        segmentation_points = [(x, y) for y, x in segmentation_points]
        original_coordinates_list.append(segmentation_points)

        # Convex Hull 좌표 추출
        hull_points = get_coordinate(segmentation_points)
        convex_coordinates_list.append(hull_points)

        # Polygon 시각화
        cv2.drawContours(polygon_img, [np.array(hull_points)], -1, (0, 255, 0), 2)  # 초록색 폴리곤
        for point in hull_points:
            cv2.circle(polygon_img, tuple(point), 5, (0, 0, 255), -1)  # 빨간 점 표시

# 6. Polygon 처리 결과 저장
cv2.imwrite(output_polygon_path, polygon_img)
print(f"Polygon result saved to {output_polygon_path}")

# 7. Convex Hull 좌표 저장
with open(output_coords_path, 'w') as f:
    for coords in convex_coordinates_list:
        f.write(','.join([f"{x[0]} {x[1]}" for x in coords]) + '\n')
print(f"Convex Hull coordinates saved to {output_coords_path}")

# 8. 원본 좌표 저장
with open(output_orig_coords_path, 'w') as f:
    for coords in original_coordinates_list:
        f.write(';'.join([f"{x[0]} {x[1]}" for x in coords]) + '\n')  # 세미콜론으로 구분
print(f"Original coordinates saved to {output_orig_coords_path}")

# 9. 결과 확인 (선택적)
plt.imshow(cv2.cvtColor(polygon_img, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()