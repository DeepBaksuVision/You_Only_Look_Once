import numpy as np
import torch
import imgaug as ia

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

num_classes = 1

def one_hot(output , label):

    label = label.cpu().data.numpy()
    b, s1, s2, c = output.shape
    dst = np.zeros([b,s1,s2,c], dtype=np.float32)

    for k in range(b):
        for i in range(s1):
            for j in range(s2):

                dst[k][i][j][int(label[k][i][j])] = 1.

    return torch.from_numpy(dst)


def detection_collate_with_size(batch):
    r"""Puts each data field into a tensor with outer dimension batch size"""
    targets = []
    imgs = []
    sizes = []
    #print(len(batch[0]))
    for sample in batch:
        imgs.append(sample[0])
        #sizes.append(sample[2])
        
        #Add Size
        #shape_np = sample[2]
        #shape = torch.Tensor(shape_np)
        sizes.append(sample[2])
        
        np_label = np.zeros((7,7,6), dtype=np.float32)
        for i in range(7):
            for j in range(7):
                np_label[i][j][1] = (num_classes-1)
        
        for object in sample[1]:
            objectness=1
            #print(len(object))
            cls = object[0]
            x_ratio = object[1]
            y_ratio = object[2]
            w_ratio = object[3]
            h_ratio = object[4]
            
            # can be acuqire grid (x,y) index when divide (1/S) of x_ratio
            grid_x_index = int(x_ratio // (1/7))
            grid_y_index = int(y_ratio // (1/7))
            x_offset = x_ratio - ((grid_x_index) * (1/7))
            y_offset = y_ratio - ((grid_y_index) * (1/7))

            # insert object row in specific label tensor index as (x,y)
            # object row follow as
            # [objectness, class, x offset, y offset, width ratio, height ratio]
            np_label[grid_x_index-1][grid_y_index-1] = np.array([objectness, cls, x_offset, y_offset, w_ratio, h_ratio])

        label = torch.from_numpy(np_label)
        targets.append(label)

    return torch.stack(imgs,0), torch.stack(targets, 0), sizes


# visdom function

def create_vis_plot(viz, _xlabel, _ylabel, _title, _legend):
    return viz.line(
        X=torch.zeros((1,)).cpu(),
        Y=torch.zeros((1, 1)).cpu(),
        opts=dict(
            xlabel=_xlabel,
            ylabel=_ylabel,
            title=_title,
            legend=_legend
        )
    )

def update_vis_plot(viz, iteration, loss, window1, window2, update_type,
                    epoch_size=1):
    viz.line(
        X=torch.ones((1, 1)).cpu() * iteration,
        Y=torch.Tensor([loss]).unsqueeze(0).cpu() / epoch_size,
        win=window1,
        update=update_type
    )


def save_checkpoint(state, is_best, filename='checkpoint.pth.tar'):
    torch.save(state, filename)
    if is_best:
        shutil.copyfile(filename, 'model_best.pth.tar')

def one_hot(output , label):

    label = label.cpu().data.numpy()
    b, s1, s2, c = output.shape
    dst = np.zeros([b,s1,s2,c], dtype=np.float32)

    for k in range(b):
        for i in range(s1):
            for j in range(s2):

                dst[k][i][j][int(label[k][i][j])] = 1.

    return torch.from_numpy(dst)

def CvtCoordsXXYY2XYWH(image_width, image_height, xmin, xmax, ymin, ymax):
    #calculate bbox_center
    bbox_center_x = (xmin + xmax) / 2 
    bbox_center_y = (ymin + ymax) / 2

    #calculate bbox_size
    bbox_width = xmax - xmin  
    bbox_height = ymax - ymin 
            
    #normalize
    normalized_x = bbox_center_x / image_width 
    normalized_y = bbox_center_y / image_height
    normalized_w = bbox_width / image_width 
    normalized_h = bbox_height / image_height 
    
    return normalized_x, normalized_y, normalized_w, normalized_h

def CvtCoordsXYWH2XXYY(normed_lxywh, image_width, image_height):
    centered_x = normed_lxywh[1] * image_width
    centered_y = normed_lxywh[2] * image_height
    object_width = normed_lxywh[3] * image_width
    object_height = normed_lxywh[4] * image_height
            
    xmin = centered_x - object_width / 2
    xmax = centered_x + object_width / 2
    ymin = centered_y - object_height / 2
    ymax = centered_y + object_height / 2
    
    return xmin, xmax, ymin, ymax

def GetImgaugStyleBBoxes(normed_lxywhs, image_width, image_height):
    bbs = ia.BoundingBoxesOnImage([], shape=(image_width,image_height))
        
    for normed_lxywh in normed_lxywhs:
        xxyy = CvtCoordsXYWH2XXYY(normed_lxywh, image_width, image_height)
        bbs.bounding_boxes.append(ia.BoundingBox(x1=xxyy[0], x2=xxyy[1], y1=xxyy[2], y2=xxyy[3], label='None'))
        
    return bbs

def GetYoloStyleBBoxes(bbs_aug, image_width, image_height):
    normed_bbs_aug = []
        
    for i in range(len(bbs_aug.bounding_boxes)):
        after = bbs_aug.bounding_boxes[i]
        coord = CvtCoordsXXYY2XYWH(image_width, image_height, xmin = after.x1, xmax = after.x2, ymin = after.y1, ymax = after.y2)
        normed_bbs_aug.append([0, round(coord[0],3), round(coord[1],3), round(coord[2],3), round(coord[3],3)])
        
    return normed_bbs_aug

def visualize_GT(images, labels, cls_list):
    Ibatch, Iw, Ih, Ic = images.shape
    Lbatch, Lw, Lh, Lc = labels.shape

    assert (Ibatch == Lbatch)

    images = torch.mul(images, 255)

    for i in range(Ibatch):
        image = images.type(torch.ByteTensor)

        img = image[i, :, :, :].cpu().data.numpy()
        label = labels[i, :, :].cpu().data.numpy()

        # Draw 7x7 Grid in Image
        dx = Iw // 7
        dy = Ih // 7

        color = np.array([255, 0, 0])

        img[:,:: dy] = color
        img[::dx,:] = color

        #print(label.shape)
        #print(label[:,:,0])

        obj_coord = label[:,:,0]
        cls = label[:,:,1]
        x_shift = label[:,:,2]
        y_shift = label[:, :, 3]
        w_ratio = label[:, :, 4]
        h_ratio = label[:, :, 5]

        _img= Image.fromarray(img, 'RGB')
        draw = ImageDraw.Draw(_img)

        for i in range(7):
            for j in range(7):
                if obj_coord[i][j] == 1:

                    x_center = dx*i + int(dx*x_shift[i][j])
                    y_center = dy*j + int(dy*y_shift[i][j])
                    width = int(w_ratio[i][j] * Iw)
                    height = int(h_ratio[i][j] * Ih)

                    xmin = x_center - (width//2)
                    ymin = y_center - (height//2)
                    xmax = xmin + width
                    ymax = ymin + height

                    draw.rectangle(((xmin, ymin),(xmax, ymax)), outline="blue")

                    draw.rectangle(((dx * i, dy * j), (dx * i + dx, dy * j + dy)), outline='#00ff88')
                    draw.ellipse(((x_center - 2, y_center - 2),
                                  (x_center + 2, y_center + 2)),
                                 fill='blue')
                    draw.text((dx * i, dy * j), cls_list[int(cls[i][j])])

        plt.figure()
        plt.imshow(_img)
        plt.show()
        plt.close()