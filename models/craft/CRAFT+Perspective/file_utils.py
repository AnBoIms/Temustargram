# -*- coding: utf-8 -*-
import os
import numpy as np
import cv2
import imgproc
from coordinates import parse_coordinates, group_by_y_coordinates, assign_regions

# borrowed from https://github.com/lengstrom/fast-style-transfer/blob/master/src/utils.py
def get_files(img_dir):
    imgs, masks, xmls = list_files(img_dir)
    return imgs, masks, xmls

def read_coordinates_from_txt(txt_file):
    """ 텍스트 파일에서 좌표를 읽어오는 함수 """
    coordinates = []
    with open(txt_file, 'r') as file:
        for line in file.readlines():
            # 각 좌표를 정수로 변환하고 리스트에 추가
            if line.strip():  # 공백 줄을 무시
                coords = list(map(int, line.strip().split(',')))
                coordinates.append(coords)
    return coordinates

def list_files(in_path):
    img_files = []
    mask_files = []
    gt_files = []
    for (dirpath, dirnames, filenames) in os.walk(in_path):
        for file in filenames:
            filename, ext = os.path.splitext(file)
            ext = str.lower(ext)
            if ext == '.jpg' or ext == '.jpeg' or ext == '.gif' or ext == '.png' or ext == '.pgm':
                img_files.append(os.path.join(dirpath, file))
            elif ext == '.bmp':
                mask_files.append(os.path.join(dirpath, file))
            elif ext == '.xml' or ext == '.gt' or ext == '.txt':
                gt_files.append(os.path.join(dirpath, file))
            elif ext == '.zip':
                continue
    # img_files.sort()
    # mask_files.sort()
    # gt_files.sort()
    return img_files, mask_files, gt_files

def crop_box_area(img, coords):
    """ 주어진 다각형 좌표로 이미지를 크롭하는 함수 """
    # 좌표를 다각형의 2D 형태로 변환
    poly = np.array(coords).reshape((-1, 2))  # 좌표 배열을 (N, 2) 형태로 변환

    # 다각형의 bounding box (최소 사각형 영역) 구하기
    x, y, w, h = cv2.boundingRect(poly)

    # 이미지에서 해당 영역을 크롭
    cropped_img = img[y:y + h, x:x + w]
    return cropped_img

def saveResult(img_file, img, boxes, dirname='./result/', verticals=None, texts=None):
        """ save text detection result one by one
        Args:
            img_file (str): image file name
            img (array): raw image context
            boxes (array): array of result file
                Shape: [num_detections, 4] for BB output / [num_detections, 4] for QUAD output
        Return:
            None
        """
        img = np.array(img)

        # make result file list
        filename, file_ext = os.path.splitext(os.path.basename(img_file))

        # result directory
        res_dict = os.path.join(dirname, f"res_{filename}")  # 안전한 경로 생성
        os.makedirs(res_dict, exist_ok=True)  # 디렉토리 생성, 이미 존재하면 건너뜀

        res_file = os.path.join(res_dict, f"res_{filename}.txt")  # 텍스트 결과 파일
        res_img_file = os.path.join(res_dict, f"res_{filename}.jpg")  # 이미지 결과 파일

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        with open(res_file, 'w') as f:
            for i, box in enumerate(boxes):
                poly = np.array(box).astype(np.int32).reshape((-1))
                strResult = ','.join([str(p) for p in poly]) + '\r\n'
                f.write(strResult)
                print(strResult)



                # poly = poly.reshape(-1, 2)
                # #cv2.polylines(img, [poly.reshape((-1, 1, 2))], True, color=(0, 0, 255), thickness=2)
                # ptColor = (0, 255, 255)
                # if verticals is not None:
                #     if verticals[i]:
                #         ptColor = (255, 0, 0)
                #
                # if texts is not None:
                #     font = cv2.FONT_HERSHEY_SIMPLEX
                #     font_scale = 0.5
                #     cv2.putText(img, "{}".format(texts[i]), (poly[0][0]+1, poly[0][1]+1), font, font_scale, (0, 0, 0), thickness=1)
                #     cv2.putText(img, "{}".format(texts[i]), tuple(poly[0]), font, font_scale, (0, 255, 255), thickness=1)

        if img is None:
            print("Error: Image is None")
            return

            #################
        txt_file = res_file  # 텍스트 파일 경로 수정
        coordinates = read_coordinates_from_txt(txt_file)
        #
        # coordinates = parse_coordinates(coordinate_data)
        # grouped_coords = group_by_y_coordinates(coordinates, y_threshold=15)
        # regions = assign_regions(grouped_coords)
        #
        # for region, coords in regions.items():
        #     print(f"{region}: {coords} : {len(coords)}")

            # 이미지를 불러옵니다 (예시로 500x500 크기 이미지 생성)
        #img = np.ones((500, 500, 3), dtype=np.uint8) * 255  # 흰색 배경

            # 각 좌표를 이미지에 폴리곤 형태로 그립니다.
        for coords in coordinates:
            poly = np.array(coords).reshape((-1, 2))  # 좌표 배열을 (N, 2) 형태로 변환
           # cv2.polylines(img, [poly], isClosed=True, color=(0, 0, 255), thickness=2)  # 빨간색 선으로 다각형 그리기

        for i, coords in enumerate(coordinates):
            cropped_img = crop_box_area(img, coords)  # Crop the polygon region
            cropped_img_file = os.path.join(res_dict, f"cropped_{i + 1}.jpg")  # Cropped image file
            cv2.imwrite(cropped_img_file, cropped_img)  # Save cropped image
            print(f"Cropped image saved: {cropped_img_file}")

        # 결과 이미지를 파일로 저장
        cv2.imwrite(res_img_file, img)
        ###################################
        # Save result image
        print(f"Result image saved: {res_img_file}")

        return res_file
