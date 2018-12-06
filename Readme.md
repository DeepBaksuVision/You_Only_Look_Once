# A PyTorch implementation of a YOLO v1 Object Detector
 Implementation of YOLO v1 object detector in PyTorch. Full tutorial can be found [here](https://deepbaksuvision.github.io/Modu_ObjectDetection/) in korean.

 Tested under Python 3.6, PyTorch 0.4.1 on Ubuntu 16.04, Windows10.

## prerequisites

- python >= 3.6
- pytorch >= 1.0.0 (1.0.0 also fine)
- torchvision >= 0.2.0
- matplotlib
- numpy
- opencv
- visdom (for visualization training process)
- wandb (for visualization training process)

NOTICE: different versions of Pytorch package have different memory usages.

## How to use
### Training on PASCAL VOC (20 classes)
```
main.py --mode train -data_path where/your/dataset/is --class_path ./names/VOC.names --num_class 20 --use_augmentation True --use_visdom True
```

### Test on PASCAL VOC (20 classes)
```
main.py  --mode test --data_path where/your/dataset/is --class_path ./names/VOC.names --num_class 20 --checkpoint_path your_checkpoint.pth.tar
```

## Supported Datasets
Only Pascal VOC datasets are supported for now.

## Configuration Options

## Results 
Todo: Result Images here!!

## Authorship
This project is equally contributed by [Chanhee Jeong](https://github.com/chjeong530), [Donghyeon Hwang](https://github.com/ssaru), and [Jaewon Lee](https://github.com/insurgent92).

## Pre-trained models
Todo: model here!  

## Copyright
See [LICENSE](./LICENSE) for details.

## REFERENCES
[1] Redmon, Joseph, et al. "You only look once: Unified, real-time object detection." Proceedings of the IEEE conference on computer vision and pattern recognition. 2016. (https://arxiv.org/abs/1506.02640)
