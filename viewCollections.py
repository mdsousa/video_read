import os
import time
import cv2
import numpy as np
from PIL import Image

collections = '20140702-192339445'
root = '/opt/collection/'

rightPath = root+collections+'/right/'
leftPath = root+collections+'/left/'

pauseTime = 0.2

leftcontent = {}
for leftitem in os.listdir(leftPath):
    leftcontent[leftitem] = os.path.getmtime(leftPath+leftitem)
#    print(content[item])

leftitems = leftcontent.keys()
leftitems.sort(lambda x,y: cmp(leftcontent[x],leftcontent[y]))
#for leftitem in leftitems:
#    print(leftitem)

rightcontent = {}
for rightitem in os.listdir(rightPath):
    rightcontent[rightitem] = os.path.getmtime(rightPath+rightitem)

rightitems = rightcontent.keys()
rightitems.sort(lambda x,y: cmp(rightcontent[x],rightcontent[y]))
#for rightitem in rightitems:
#    print(rightitem)

cv2.namedWindow(collections, cv2.WINDOW_NORMAL)

for l,r in zip(leftitems,rightitems):
    leftim = cv2.imread(leftPath+l,cv2.CV_LOAD_IMAGE_COLOR)
#    print(leftPath+l)
#    print(leftim.shape)

    rightim = cv2.imread(rightPath+r,cv2.CV_LOAD_IMAGE_COLOR)
#    print(rightPath+r)
#    print(rightim.shape)

    # iml = np.array(leftim)
    # imlcv = iml[:, :, ::-1].copy()
    # imr = np.array(rightim)
    # imrcv = imr[:, :, ::-1].copy()
    # collection = np.hstack( (imlcv,imrcv) )
#    leftim = cv2.cvtColor(leftim, cv2.COLOR_RGB2BGR)
#    rightim = cv2.cvtColor(rightim, cv2.COLOR_RGB2BGR)

    collection = np.hstack( (leftim,rightim) )
    cv2.imshow(collections,collection)
    cv2.waitKey(200)

cv2.destroyAllWindows()
#    time.sleep(pauseTime)

