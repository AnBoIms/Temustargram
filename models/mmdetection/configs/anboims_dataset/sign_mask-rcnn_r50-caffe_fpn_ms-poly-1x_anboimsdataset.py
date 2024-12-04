_base_ = '../mask_rcnn/mask-rcnn_r50-caffe_fpn_ms-poly-1x_coco.py'

model = dict(
    roi_head=dict(
        bbox_head=dict(num_classes=1), mask_head=dict(num_classes=1)))

metainfo = {
    'classes': ('0', ),
    'palette': [
        (220, 20, 60),
    ]
}