import cv2
import numpy as np

#Convex Hull coordinate extract function
def get_coordinate(segmentation_points):
    points = np.array(segmentation_points, dtype=np.float32)
    hull = cv2.convexHull(points)
    rect = cv2.minAreaRect(hull)
    box = cv2.boxPoints(rect)
    return np.int0(box).tolist()
