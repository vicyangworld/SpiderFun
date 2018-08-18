# -*- coding: utf-8 -*-

import glob as gb
import cv2
import re
import numpy as np
import time

path = r"C:\\Users\\orion\\yangwenkui\\practices\\SpiderFun\AQI\\"
imglist = gb.glob(path+"*.jpeg")
imgWidth  = 2400
imgHeight = 1200 * 2
videoWriter = cv2.VideoWriter(path+'test.mp4',cv2.VideoWriter_fourcc(*'XVID') , 10, (imgWidth,imgHeight))

labelFile=r"C:\\Users\\orion\\yangwenkui\\practices\\SpiderFun\AQI\\label.jpeg"
labelImg = cv2.imread(labelFile)

# objFile=r"C:\\Users\\orion\\yangwenkui\\practices\\SpiderFun\AQI\\2015-01-01-s.jpeg"
# objImg = cv2.imread(objFile)

# print(labelImg.shape)
# print(objImg.shape)
#cv2.imshow("截取", objImg[700:1089,400:626])
# objImg[1570:2388,370:747] = labelImg
# #cv2.imshow("new", objImg)
# cv2.imwrite(path+"new.jpg", objImg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

count = 0
length = len(imglist)
start = time.time()
for file in imglist:
    if file.endswith('-s.jpeg'):
        # print("processing \t",count," / ", length)
        img1  = cv2.imread(file) 
        img1[1570:2388,370:747] = img1[1,1]
        img2  = cv2.imread(file.split('.')[0][:-2]+'.jpeg')
        img2[1570:2388,370:747] = img2[1,1]
        img2[100:300,200:3050] = img2[1,1]
        img = np.concatenate((img1, img2))
        img[1970:2788,370:747] = labelImg
        # cv2.imshow("new", img)
        # print(img.shape)
        img = cv2.resize(img,(imgWidth,imgHeight))
        # cv2.imwrite(path+"new.jpg", img)
        videoWriter.write(img)
        count = count + 1
end = time.time()
print("time consuming: ",end-start, " second")