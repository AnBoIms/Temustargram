import os
import re
import torch
import imgproc
import craft_utils
import file_utils
from craft import CRAFT
from refinenet import RefineNet
from torch.autograd import Variable
from collections import OrderedDict
import cv2


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

def sanitize_filename(filename):
    """ 파일 이름에서 유효하지 않은 문자를 제거 """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def test_net(net, image, text_threshold, link_threshold, low_text, poly, mag_ratio, canvas_size, refine_net=None):
    # resize
    img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(
        image, canvas_size, interpolation=cv2.INTER_LINEAR, mag_ratio=mag_ratio
    )
    ratio_h = ratio_w = 1 / target_ratio

    # preprocessing
    x = imgproc.normalizeMeanVariance(img_resized)
    x = torch.from_numpy(x).permute(2, 0, 1)    # [h, w, c] to [c, h, w]
    x = Variable(x.unsqueeze(0))                # [c, h, w] to [b, c, h, w]

    # forward pass
    with torch.no_grad():
        y, feature = net(x)

    # make score and link map
    score_text = y[0, :, :, 0].cpu().data.numpy()
    score_link = y[0, :, :, 1].cpu().data.numpy()

    # refine link
    if refine_net is not None:
        with torch.no_grad():
            y_refiner = refine_net(y, feature)
        score_link = y_refiner[0, :, :, 0].cpu().data.numpy()

    # Post-processing
    boxes, polys = craft_utils.getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)

    # coordinate adjustment
    boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
    polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
    for k in range(len(polys)):
        if polys[k] is None:
            polys[k] = boxes[k]

    return boxes, polys


def run_craft(image_path, result_folder, model_path='./craft_mlt_25k.pth', text_threshold=0.7, low_text=0.4,
              link_threshold=0.4, canvas_size=1280, mag_ratio=1.5, poly=False, refine=False, refiner_model=None):
    # load model
    net = CRAFT()
    net.load_state_dict(copyStateDict(torch.load(model_path, map_location='cpu')))
    net.eval()

    # load image
    image = imgproc.loadImage(image_path)

    # LinkRefiner
    refine_net = None
    if refine:
        refine_net = RefineNet()
        refine_net.load_state_dict(copyStateDict(torch.load(refiner_model, map_location='cpu')))
        refine_net.eval()

    # run test
    bboxes, polys = test_net(net, image, text_threshold, link_threshold, low_text, poly, mag_ratio, canvas_size, refine_net)

    # save result
    sanitized_filename = sanitize_filename(os.path.splitext(os.path.basename(image_path))[0])
    file_utils.saveResult(image_path, image[:, :, ::-1], polys, dirname=result_folder)

    return polys
