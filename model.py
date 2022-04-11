import torch
import torchvision
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import uuid
import os

from config import UPLOAD_FOLDER, MODEL_PATH

def apply_nms(orig_prediction, iou_thresh=0.2):
    # torchvision returns the indices of the bboxes to keep
    keep = torchvision.ops.nms(orig_prediction['boxes'], orig_prediction['scores'], iou_thresh)

    final_prediction = orig_prediction
    final_prediction['boxes'] = final_prediction['boxes'][keep]
    final_prediction['scores'] = final_prediction['scores'][keep]
    final_prediction['labels'] = final_prediction['labels'][keep]

    return final_prediction


# function to convert a torchtensor back to PIL image
def torch_to_pil(img):
    # return Image.open(image).convert('RGB')
    return Image.open(img).convert('RGB')

def plot_img_bbox(img, target):
    # plot the image and bboxes
    # Bounding boxes are defined as follows: x-min y-min width height
    fig, a = plt.subplots(1,1)
    fig.set_size_inches(15,15) # fig.set_size_inches(5,5)
    a.imshow(img)
    for e, label in enumerate(target['labels']):
        x, y, width, height  = target['boxes'][e][0], target['boxes'][e][1], target['boxes'][e][2]-target['boxes'][e][0], target['boxes'][e][3]-target['boxes'][e][1]


        if label == 1:
            rect = patches.Rectangle((x, y),
                                     width, height,
                                     linewidth = 4,
                                     edgecolor = 'lime',
                                     facecolor = 'none')
        else:
            rect = patches.Rectangle((x, y),
                                     width, height,
                                     linewidth = 4,
                                     edgecolor = 'orangered',
                                     facecolor = 'none')

        # Draw the bounding box on top of the image
        a.add_patch(rect)

    file_name = f'{uuid.uuid4().hex}.jpg'
    plt.savefig(os.path.join(UPLOAD_FOLDER, file_name), bbox_inches='tight', pad_inches=0)

    return file_name


def predict_cells(image):
    model = torch.load(MODEL_PATH, map_location='cpu')
    model.eval()

    data_transform = transforms.Compose([transforms.ToTensor()])
    img = Image.open(image).convert('RGB')
    img_tensor = data_transform(img).unsqueeze(0)


    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    # model.eval()
    with torch.no_grad():
        prediction = model(img_tensor)[0]

    nms_prediction = apply_nms(prediction, iou_thresh=0.2)

    pred = {}
    pred['boxes'] = nms_prediction['boxes'].numpy()
    pred['scores'] = nms_prediction['scores'].numpy()
    pred['labels'] = nms_prediction['labels'].numpy()

    pred_boxes = {}
    pred_boxes['boxes'] = []
    pred_boxes['labels'] = []
    for e, score in enumerate(pred['scores']):
        if score > 0.1:
            pred_boxes['boxes'].append(pred['boxes'][e])
            pred_boxes['labels'].append(pred['labels'][e])

    pic = plot_img_bbox(torch_to_pil(image), pred_boxes)

    # print(pred_boxes['labels'].count(1))
    # print(pred_boxes['labels'].count(2))

    return pred_boxes['labels'].count(1), pred_boxes['labels'].count(2), pic

def concentrate(dilution, n_square, alive, dead):
  return int(5000*int(dilution)*alive/n_square), int(5000*int(dilution)*(alive+dead)/n_square)

def alive_cells(alive, dead):
  return int(alive*100/(alive+dead))

