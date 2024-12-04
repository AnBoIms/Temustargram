import cv2
import numpy as np

#Convex Hull 좌표 추출 함수
def get_coordinate(segmentation_points):
    points = np.array(segmentation_points, dtype=np.float32)
    hull = cv2.convexHull(points)
    rect = cv2.minAreaRect(hull)
    box = cv2.boxPoints(rect)
    return np.int0(box).tolist()
