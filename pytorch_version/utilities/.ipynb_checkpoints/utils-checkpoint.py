import numpy as np
import torch

num_classes = 1


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

def augmentImage(image, normed_lxywhs, image_width, image_height, seq):
    
    bbs = GetImgaugStyleBBoxes(normed_lxywhs, image_width, image_height)
         
    seq_det = seq.to_deterministic()
        
    image_aug = seq_det.augment_images([image])[0]
    
    bbs_aug = seq_det.augment_bounding_boxes([bbs])[0]
    
    if(True):
        image_before = bbs.draw_on_image(image, thickness=5)
        image_after = bbs_aug.draw_on_image(image_aug, thickness=5, color=[0, 0, 255])
        
        fig = plt.figure(1, (10., 10.))
        grid = ImageGrid(fig, 111,  # similar to subplot(111)
                 nrows_ncols=(1, 2),  # creates 2x2 grid of axes
                 axes_pad=0.1,  # pad between axes in inch.
                 )
        
        #grid[0].imshow(image_before)
        #grid[1].imshow(image_after)
        #plt.show()
        
    normed_bbs_aug = GetYoloStyleBBoxes(bbs_aug, image_width, image_height)
            
    
    return image_aug, normed_bbs_aug

