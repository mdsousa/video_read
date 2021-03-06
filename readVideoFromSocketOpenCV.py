import cv2
import io
import socket
import struct
import numpy
from PIL import Image

ss = socket.socket()
ss.bind(('0.0.0.0',5001))
ss.listen(0)

connection = ss.accept()[0].makefile('rb')
#fd = connection.fileno()
#print('fd: %d\n' %fd)
#print('connection: %s\n' % connection)
try:
    cv2.namedWindow('From PI', cv2.WINDOW_NORMAL)
    video_stream = io.BytesIO()
    image_len = struct.unpack('<L', connection.read(4))[0]
    video_stream.write(connection.read(image_len))
#    cap = cv2.VideoCapture(connection)
    cap = cv2.VideoCapture(video_stream.read(image_len))
#    print('open: %s\n' % cap.open(video_stream))
#    print('is opened: %s\n' % cap.isOpened())
    ret, frame = cap.read(numpy.array(video_stream.read(image_len)))
#    ret, frame = cap.read(video_stream.read(image_len))
    print('Frame size: %dx%d' % frame.size)
    while cap.isOpened():
        video_stream.write(connection.read(image_len))
        ret, frame = cap.read(video_stream.read(image_len))
        print('Frame size: %dx%d' % frame.size)
        cv2.imshow('From PI', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release

    # while True:
    #     # unpack the python struck as long integer, litte endian
    #     image_len = struct.unpack('<L',connection.read(4))[0]
    #     if not image_len:
    #         break
    #     image_stream = io.BytesIO()
    #     image_stream.write(connection.read(image_len))
    #     # Rewind the stream, open it as an image with PIL and do some
    #     # processing on it
    #     image_stream.seek(0)
    #     image = Image.open(image_stream)
    #     # convert PIL to opencv
    #     imgnp = numpy.array(image)
    #     imgcv = imgnp[:, :, ::-1].copy()
#        imgcv = cv2.imdecode(imgnp, 0)
#        print('Image size: %dx%d' % image.size)
#        image.verify()
#        print('Image is verified\n')
#        if len(imgcv) > 0:
#            print('Image length: %d' % len(imgcv))
#            cv2.imshow('From PI',imgcv)
#            cv2.waitKey(1)

finally:
    connection.close()
    ss.close()
    cv2.destroyAllWindows()
