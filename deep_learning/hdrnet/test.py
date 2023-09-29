import os
import sys
import cv2
import numpy as np
import skimage.exposure
import torch
from torchvision import transforms

from model import HDRPointwiseNN
from utils import load_image, resize, load_params
import matplotlib.pyplot as plt

def test(ckpt, args={}):
    state_dict = torch.load(ckpt)
    state_dict, params = load_params(state_dict)
    params.update(args)

    device = torch.device("cuda")
    tensor = transforms.Compose([
        transforms.ToTensor(),
    ])
    imgs=os.listdir(params['test_image'])
    for xxx in imgs:
        imgpath=os.path.join(params['test_image'],xxx)
        low = tensor(resize(load_image(imgpath),params['net_input_size'],strict=True).astype(np.float32)).repeat(1,1,1,1)/255
        full = tensor(load_image(imgpath).astype(np.float32)).repeat(1,1,1,1)/255
        
        low = low.to(device)
        full = full.to(device)
        with torch.no_grad():
            model = HDRPointwiseNN(params=params)
            model.load_state_dict(state_dict)
            model.eval()
            model.to(device)
            img = model(low, full)
            print('MIN:',torch.min(img),'MAX:',torch.max(img))
            img = (img.cpu().detach().numpy()).transpose(0,2,3,1)[0]
            img = skimage.exposure.rescale_intensity(img, out_range=(0.0,255.0)).astype(np.uint8)
            print(os.path.join(params['test_out'],xxx))
            cv2.imwrite(os.path.join(params['test_out'],xxx), img[...,::-1])

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='HDRNet Inference')
    parser.add_argument('--checkpoint', type=str, help='model state path')
    parser.add_argument('--input', type=str, dest="test_image", help='image path')
    parser.add_argument('--output', type=str, dest="test_out", help='output image path')

    args = vars(parser.parse_args())
    # args['checkpoint']="./ch/ckpt_9_10199.pth"
    # args['input']='../DeepUPE_pytorch/mixed/sample_imgs'
    # args['output']='./sample_results'
    # python test.py --checkpoint ./ch/ckpt_9_10199.pth --input ../DeepUPE_pytorch/sample_imgs --output ./sample_results
    test(args['checkpoint'], args)