# A PyTorch implementation of a YOLO v1 Object Detector
 Implementation of YOLO v1 object detector in PyTorch (TF-Slim). Full tutorial can be found [here](https://deepbaksuvision.github.io/Modu_ObjectDetection/) in korean.

 Tested under Python 3.6, PyTorch 0.4.1 on Ubuntu 16.04, Windows10.

## prerequisites

- Python >= 3.6
- Pytorch >= 0.4.3 


Tested under python3.

python packages
pytorch>=0.3.1
torchvision>=0.2.0
cython
matplotlib
numpy
scipy
opencv
pyyaml
packaging
pycocotools — for COCO dataset, also available from pip.
tensorboardX — for logging the losses in Tensorboard
An NVIDAI GPU and CUDA 8.0 or higher. Some operations only have gpu implementation.
NOTICE: different versions of Pytorch package have different memory usages.

## How to use
Testi
Training on PASCAL VOC 
## Supported Datasets
Only COCO is supported for now. However, the whole dataset library implementation is almost identical to Detectron's, so it should be easy to add more datasets supported by Detectron.

## Configuration Options

## Results 
## Authorship
This project is equally contributed by [Chanhui Jeong](https://github.com/chjeong530), [Donghyeon Hwang](https://github.com/ssaru), and [Jaewon Lee](https://github.com/insurgent92).

## Pre-trained models     

## Copyright
See [LICENSE](./LICENSE) for details.
## REFERENCES
[1] Redmon, Joseph, et al. "You only look once: Unified, real-time object detection." Proceedings of the IEEE conference on computer vision and pattern recognition. 2016.
