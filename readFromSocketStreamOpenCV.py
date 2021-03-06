import cv2
import io
import socket
import struct
import numpy
import thread
import Tkinter
import Queue
from PIL import Image


ss = socket.socket()
ss.bind(('0.0.0.0',5001))
ss.listen(0)

connection = ss.accept()[0].makefile('rb')

def listenForKey(event):
    while True:
        s = raw_input()
        if
    if event.keysym == 'Escape':
        
    

s1 = socket.socket()
s1.bind( ('0.0.0.0', 5003) )
ss.listen(0)

try:
    cv2.namedWindow('From PI', cv2.WINDOW_NORMAL)
    while True:
        # unpack the python struck as long integer, litte endian
        image_len = struct.unpack('<L',connection.read(4))[0]
        if not image_len:
            break
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        # convert PIL to opencv
        imgnp = numpy.array(image)
        imgcv = imgnp[:, :, ::-1].copy()

#        imgcv = cv2.imdecode(imgnp, 0)
#        print('Image size: %dx%d' % image.size)
#        image.verify()
#        print('Image is verified\n')

        # now that we have our opencv frame, let's
        # do some processing on it
        if len(imgcv) > 0:
#            print('Image length: %d' % len(imgcv))
            gray = cv2.cvtColor(imgcv, cv2.COLOR_BGR2GRAY)
            edges = cv2.GaussianBlur(gray, (3,3), 0)
            edges = cv2.Canny(edges,100,200)
#            edges = cv2.Canny(edges,75,200,apertureSize=3, L2gradient=True)
#            print imgcv[:,:].size
            print imgcv.shape
            print edges.shape
            print gray.shape
#            mergedImg = cv2.bitwise_and(imgcv,imgcv,mask=edges)
            # print('imgcv size: %d' % imgcv.size)
            # print('edges size: %d' % edges.size)
            print('\n\n')
#            detections = cv2.add(imgcv,edges)
            imgedges = imgcv.copy()
#            imgedges[edges != 0] = (0,255,0) # green
            imgedges[edges != 0] = (255,255,0) # yellow
            cv2.imshow('From PI', imgedges)
#            cv2.imshow('From PI', gray)
#            cv2.imshow('From PI', mergedImg)
#            cv2.imshow('From PI',detections)
#            cv2.imshow('From PI',imgcv)
            cv2.waitKey(1)
            
finally:
    connection.close()
    ss.close()
    cv2.destroyAllWindows()
