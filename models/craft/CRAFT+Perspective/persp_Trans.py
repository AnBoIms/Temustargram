import numpy as np
import cv2


def read_coorTxt(file_path: str):
    """
    Reads a text file containing coordinates and parses them into a numpy array.
    
    Args:
        file_path (str): The path to the .txt file containing the coordinates in "x1 y1,x2 y2,..." format.
        
    Returns:
        np.float32: A numpy array of shape (n, 2) containing the coordinates.
    """
    try:
        with open(file_path, 'r') as file:
            # Read the entire content of the file
            coordinates = file.read().strip()
        
        # Split the string into individual coordinate pairs
        pairs = coordinates.split(',')
        
        # Parse each pair into a list of floats
        points = [list(map(int, pair.split())) for pair in pairs]
        print(points)
        # Convert to numpy array with dtype np.float32
        return np.float32(points)
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except ValueError:
        print("Error: File contains invalid format.")
        return None    

def crop_idcard(image):
    """
    Crops an ID card from the given image using perspective transformation,
    ensuring it fits a horizontal rectangle with the correct orientation.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        numpy.ndarray: The cropped and correctly oriented ID card image.
    """
    # 이미지 읽기
    img = image
    h, w = img.shape[:2]

    if img is None:
        raise ValueError("Image not found or invalid. Please check the input.")

    # 원본 좌표 정의
    # pts1 = np.float32([
    #     [901, 2091],
    #     [1156,1687],
    #     [1800, 2095],
    #     [1546, 2498]
    # ])
    txtfile = "./coorTxt/convex_coords.txt"
    pts1 = read_coorTxt(txtfile)



    # 왼쪽 그룹 (x값이 작은 두 점)과 오른쪽 그룹 (x값이 큰 두 점)을 분리
    pts1 = sorted(pts1, key=lambda p: p[0])  # x좌표 기준으로 정렬
    left_group = pts1[:2]  # x값이 작은 두 점
    right_group = pts1[2:]  # x값이 큰 두 점

    # 각 그룹에서 위/아래 점 찾기 (y값 기준으로 정렬)
    left_group = sorted(left_group, key=lambda p: p[1])  # y좌표 기준 정렬
    right_group = sorted(right_group, key=lambda p: p[1])  # y좌표 기준 정렬

    # 네 꼭짓점 지정 (좌상단, 좌하단, 우하단, 우상단 순서로 정렬)
    top_left = left_group[0]
    bottom_left = left_group[1]
    top_right = right_group[0]
    bottom_right = right_group[1]
    print("x-left group: ", bottom_left)

    # 정렬된 좌표 출력
    ordered_pts = np.float32([top_left, bottom_left, bottom_right, top_right])
    print("Ordered Points (Top-Left, Bottom-Left, Bottom-Right, Top-Right):")
    for i, pt in enumerate(ordered_pts):
        print(f"Point {i + 1}: {pt}")

    # 변환 후의 대상 좌표 정의
    pts2 = np.float32([[0, 0], [0, 540], [860, 540], [860, 0]])  # Target coordinates

    # 투시 변환 매트릭스 계산 및 변환 적용
    M = cv2.getPerspectiveTransform(ordered_pts, pts2)

    output_width = int(max(pts2[:, 0]) - min(pts2[:, 0]))
    output_height = int(max(pts2[:, 1]) - min(pts2[:, 1]))
    dst = cv2.warpPerspective(img, M, (output_width, output_height))

    return dst
