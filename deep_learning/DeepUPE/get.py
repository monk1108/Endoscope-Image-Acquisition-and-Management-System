import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
from scipy import signal
import cv2
import os

def SmoothingFilter(img,kernal_size=(3,3),stype='average',weight=1,sigma=3):
    size=kernal_size[0]
    pd=(size-1)//2
    row,col=img.shape
    output_img=np.zeros(img.shape)
    img_zp=np.copy(img)
    img=np.pad(img,((pd,pd),(pd,pd)),'constant',constant_values=(0,0))
    gaussian_sum=0
    if stype=='average':
        kernal=np.ones((size,size))/(size*size)
        output_img=signal.convolve2d(img_zp,kernal,'same')
    elif stype=='Weighted average':
        kernal=np.ones((size,size))/(size*size)
        kernal[pd+1,pd+1]*=weight
        output_img=signal.convolve2d(img_zp,kernal,'same')
    elif stype=='gaussian':
        kernal=gaussian_filter(size,0,sigma)
        output_img=signal.convolve2d(img_zp,kernal,'same')
    for i in range(row):
        for j in range(col):
            pixels=np.mat(img[i:i+size,j:j+size])
            if stype=='min':
                output_img[i,j]=np.min(pixels)
            elif stype=='median':
                output_img[i,j]=np.median(np.array(pixels))
            elif stype=='max':
                output_img[i,j]=np.max(pixels)
    return output_img

# def C(rk):
#   # 读取图片灰度直方图
#   # bins为直方图直方柱的取值向量
#   # hist为bins各取值区间上的频数取值
#   hist, bins = np.histogram(rk, 256, [0, 256])
#   # 计算累计分布函数
#   return hist.cumsum()
 
# # 计算灰度均衡化映射
# def T(rk):
#     cdf = C(rk)
#     # 均衡化
#     cdf = (cdf - cdf.min()) * (255 - 0) / (cdf.max() - cdf.min()) + 0
#     return cdf.astype('uint8')

def def_equalizehist(img,L=256):
    img = cv2.imread(img,0)
    cv2.imshow("ori",img)
    h, w = img.shape
    # 计算图像的直方图，即存在的每个灰度值的像素点数量
    hist = cv2.calcHist([img],[0],None,[256],[0,255])
    # 计算灰度值的像素点的概率，除以所有像素点个数，即归一化
    hist[0:255] = hist[0:255] / (h*w)
    # 设置Si
    sum_hist = np.zeros(hist.shape)
    #开始计算Si的一部分值，注意i每增大，Si都是对前i个灰度值的分布概率进行累加
    for i in range(256):
        sum_hist[i] = sum(hist[0:i+1])
    equal_hist = np.zeros(sum_hist.shape)
    #Si再乘上灰度级，再四舍五入
    for i in range(256):
        equal_hist[i] = int(((L - 1) - 0) * sum_hist[i] + 0.5)
    equal_img = img.copy()
    #新图片的创建
    for i in range(h):
        for j in range(w):
            equal_img[i, j] = equal_hist[img[i, j]]
            
    equal_hist = cv2.calcHist([equal_img], [0], None, [256], [0, 256])
    equal_hist[0:255] = equal_hist[0:255] / (h * w)
    # cv2.imshow("inverse", equal_img)
    # # 显示最初的直方图
    # #plt.figure("原始图像直方图")
    # plt.plot(hist, color='b')
    # plt.show()
    # #plt.figure("直方均衡化后图像直方图")
    # plt.plot(equal_hist, color='r')
    # plt.show()
    # cv2.waitKey()
    #return equal_hist
    return equal_img

def change_illu(img,illu):
    rows,cols,_=img.shape
    dst = np.zeros((rows,cols,3),dtype="uint8")     #新建目标图像，矩阵中每个元素的类型为uint8
    # print(illu.shape)
    for i in range(rows):
        for j in range(cols):
            B=img[i,j][0]   #获取原始图像
            G=img[i,j][1]
            R=img[i,j][2]
            
#             result = np.round(illu[i,j]/255.0*100)
            temp=illu[i,j]/255.0
            if temp!=0:
                result = np.round(temp*120)
    #             print(result)
                B=img[i,j][0]-result
                G=img[i,j][1]-result
                R=img[i,j][2]-result

                B=min(255,max(0,B))  #防止越界
                G=min(255,max(0,G))
                R=min(255,max(0,R))
                dst[i,j]=np.uint8((B,G,R))  #生成处理后的图像

    return dst

if __name__=='__main__':
    imgpath="./BKAI-IGH/input"
    img_list=os.listdir(imgpath)
    save_dir="./BKAI-IGH/degraded"
    i=0
    for imgname in img_list:
        i+=1
        img=plt.imread(os.path.join(imgpath,imgname))
        
        img_hsv=np.max(img,axis=2)
        img_hsv=img_hsv/255.0
        # print(img_hsv.shape)
        img6=SmoothingFilter(img_hsv,(100,100),'average')
        # print(img6.shape)
        img7=img6/np.max(img6)*255
        # print(img7.shape)
        # img_eq=def_equalizehist(img7)
        # print(img_eq.shape)
        img_enhance=change_illu(img,img7)
        cv2.imwrite(os.path.join(save_dir,imgname), cv2.cvtColor(img_enhance, cv2.COLOR_RGB2BGR))
        print(imgname,"            ",i/len(img_list)*100)