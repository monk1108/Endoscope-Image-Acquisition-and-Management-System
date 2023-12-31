import os 
import torch
import cv2
from glob import glob
import argparse
import warnings
import numpy as np
from utils import PSNR, validation, LossNetwork
from model.IAT_main import IAT
from torchvision.transforms import Normalize
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--file_name', type=str, default='demo_imgs/exposure_demo.JPG')
parser.add_argument('--normalize', type=bool, default=False)
parser.add_argument('--task', type=str, default='exposure', help='Choose from exposure or enhance')
config = parser.parse_args()

# Weights path
exposure_pretrain = r'best_Epoch_exposure.pth'
enhance_pretrain = r'best_Epoch_lol_v1.pth'

normalize_process = Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))

## Load Pre-train Weights
model = IAT().cuda()
if config.task == 'exposure':
    model.load_state_dict(torch.load(exposure_pretrain))
elif config.task == 'enhance':
    model.load_state_dict(torch.load(enhance_pretrain))
else:
    warnings.warn('Only could be exposure or enhance')
model.eval()

for file_name in glob("/home/sjtu/chenyuze/mydeep/DeepUPE_pytorch/sample_imgs/*"):
    ## Load Image
    # img = plt.imread(file_name)
    img=cv2.imread(file_name)
    row,col,_=img.shape
    img=cv2.resize(img,(int(col/1.0),int(row/1.0)))
    input = np.asarray(img)/255.0
    input = torch.from_numpy(input).float().cuda()
    input = input.permute(2,0,1).unsqueeze(0)
    if config.normalize:    # False
        input = normalize_process(input)

    ## Forward Network
    _, _ ,enhanced_img = model(input)
    enhanced_img = enhanced_img.cpu().squeeze(0).permute(1,2,0)
    enhanced_img = enhanced_img.detach().numpy()
    enhanced_img = (enhanced_img*255.0).astype(np.uint8)

    # plt.imshow(enhanced_img)
    # #plt.imsave('results.png', enhanced_img) 
    # plt.show()
    img_name=file_name.split('/')[-1]
    # cv2.imwrite(os.path.join("./sample_results",img_name),cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR))
    cv2.imwrite(os.path.join("./sample_results",img_name),enhanced_img)
