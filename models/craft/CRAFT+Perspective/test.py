"""  
Copyright (c) 2019-present NAVER Corp.
MIT License
"""
# -*- coding: utf-8 -*-
import sys
import os
import time
import re
import argparse
import torch
import torch.nn as nn
from torch.autograd import Variable
from PIL import Image
import cv2
from skimage import io
import numpy as np
import craft_utils
import imgproc
import file_utils
import json
import zipfile
from craft import CRAFT
from collections import OrderedDict
from persp_Trans import crop_idcard
from coordinates import assign_regions, group_by_y_coordinates, parse_coordinates

def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict

def str2bool(v):
    return v.lower() in ("yes", "y", "true", "t", "1")

def sanitize_filename(filename):
    """ 파일 이름에서 유효하지 않은 문자를 제거 """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# 경로 결합 시 중복된 슬래시를 방지하는 방법
def get_output_filepath(result_folder, filename, extension):
    """ 결과 파일 경로를 생성, 슬래시 중복 방지 """
    # 경로와 파일 이름을 안전하게 결합
    return os.path.join(result_folder, f"res_{filename}{extension}")

parser = argparse.ArgumentParser(description='CRAFT Text Detection')
parser.add_argument('--trained_model', default='weights/craft_mlt_25k.pth', type=str, help='pretrained model')
parser.add_argument('--text_threshold', default=0.7, type=float, help='text confidence threshold')
parser.add_argument('--low_text', default=0.4, type=float, help='text low-bound score')
parser.add_argument('--link_threshold', default=0.4, type=float, help='link confidence threshold')
parser.add_argument('--cuda', default=False, type=str2bool, help='Use cuda for inference')  # 기본값을 False로 설정
parser.add_argument('--canvas_size', default=1280, type=int, help='image size for inference')
parser.add_argument('--mag_ratio', default=1.5, type=float, help='image magnification ratio')
parser.add_argument('--poly', default=False, action='store_true', help='enable polygon type')
parser.add_argument('--show_time', default=False, action='store_true', help='show processing time')
parser.add_argument('--test_folder', default='/data/', type=str, help='folder path to input images')
parser.add_argument('--refine', default=False, action='store_true', help='enable link refiner')
parser.add_argument('--refiner_model', default='weights/craft_refiner_CTW1500.pth', type=str, help='pretrained refiner model')

args = parser.parse_args()

""" For test images in a folder """
image_list, _, _ = file_utils.get_files(args.test_folder)

result_folder = './result/'
if not os.path.isdir(result_folder):
    os.mkdir(result_folder)


def test_net(net, image, text_threshold, link_threshold, low_text, poly, refine_net=None):
    t0 = time.time()

    # resize
    img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(image, args.canvas_size, interpolation=cv2.INTER_LINEAR, mag_ratio=args.mag_ratio)
    ratio_h = ratio_w = 1 / target_ratio

    # preprocessing
    x = imgproc.normalizeMeanVariance(img_resized)
    x = torch.from_numpy(x).permute(2, 0, 1)    # [h, w, c] to [c, h, w]
    x = Variable(x.unsqueeze(0))                # [c, h, w] to [b, c, h, w]

    # forward pass
    with torch.no_grad():
        y, feature = net(x)

    # make score and link map
    score_text = y[0,:,:,0].cpu().data.numpy()
    score_link = y[0,:,:,1].cpu().data.numpy()

    # refine link
    if refine_net is not None:
        with torch.no_grad():
            y_refiner = refine_net(y, feature)
        score_link = y_refiner[0,:,:,0].cpu().data.numpy()

    t0 = time.time() - t0
    t1 = time.time()

    # Post-processing
    boxes, polys = craft_utils.getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)

    # coordinate adjustment
    boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
    polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
    for k in range(len(polys)):
        if polys[k] is None: polys[k] = boxes[k]

    t1 = time.time() - t1

    # render results (optional)
    render_img = score_text.copy()
    render_img = np.hstack((render_img, score_link))
    ret_score_text = imgproc.cvt2HeatmapImg(render_img)

    if args.show_time : print("\ninfer/postproc time : {:.3f}/{:.3f}".format(t0, t1))

    return boxes, polys, ret_score_text


if __name__ == '__main__':
    # load net
    net = CRAFT()     # initialize
    pretrained_model = './craft_mlt_25k.pth'
    test_folder = './img/'
    result_folder = './result/'

    text_threshold = 0.7  # 변경
    low_text = 0.4  # 변경
    link_threshold = 0.4  # 변경
    canvas_size = 1280  # 변경
    mag_ratio = 1.5  # 변경
    poly = False  # 변경

    print('Loading weights from checkpoint (' + pretrained_model + ')')
    net.load_state_dict(copyStateDict(torch.load(pretrained_model, map_location='cpu')))

    net.eval()
    image_list, _, _ = file_utils.get_files(test_folder)

    # LinkRefiner
    refine_net = None
    if args.refine:
        from refinenet import RefineNet
        refine_net = RefineNet()
        print('Loading weights of refiner from checkpoint (' + args.refiner_model + ')')
        refine_net.load_state_dict(copyStateDict(torch.load(args.refiner_model, map_location='cpu')))
        refine_net.eval()
        args.poly = True

    t = time.time()

    # load data
    for k, image_path in enumerate(image_list):
        print(f"Test image {k+1}/{len(image_list)}: {image_path}", end='\r')
        image = imgproc.loadImage(image_path)

        #------------------------------------
        image = crop_idcard(image)
        # ------------------------------------

        bboxes, polys, score_text = test_net(
            net, image, text_threshold, link_threshold, low_text, poly
        )

        # save score text
        filename, file_ext = os.path.splitext(os.path.basename(image_path))
        sanitized_filename = sanitize_filename(filename)  # 파일 이름 정리
        file_utils.saveResult(image_path, image[:,:,::-1], polys, dirname=result_folder)



    print("elapsed time : {}s".format(time.time() - t))


