import socket
import threading
import ConfigParser # read config file
import traceback
import signal
import sys
import select
import termios
import tty
import errno

import time
#import Queue
import cv2
import struct
import io
import numpy as np
import Queue
from PIL import Image

#
# For each client sending video, need a socket for sending cmds and one for retrieving data
#
client1 = None
client2 = None
cmd_socket1 = None
cmd_socket2 = None
cmd_port1 = None
cmd_port2 = None
stream_port1 = None
stream_port2 = None
stream_write_length = None
stream_socket1 = None
stream_socket2 = None
sockfd1 = None
sockfd2 = None
addr1 = None
streamThread1 = None

def signal_handler(signal, frame):
#    global key
    print("\nCtrl-C pressed")
    cleanup()
#    key = 'e'
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def readConfig():
    global client1
    global client2
    global cmd_port1
    global cmd_port2
    global stream_port1
    global stream_port2
    global stream_write_length
    try:
        parser = ConfigParser.ConfigParser()
        parser.read('config_pi_server.cfg')
        client1 = parser.get('configuration','client1')
#        print('client1: %s' % client1)
        client2 = parser.get('configuration','client2')
#        print('client2: %s' % client2)
        cmd_port1 = int(parser.get('configuration','cmd_port1'))
        cmd_port2 = int(parser.get('configuration','cmd_port2'))
        stream_port1 = int(parser.get('configuration','stream_port1'))
        stream_port2 = int(parser.get('configuration','stream_port2'))
        stream_write_length = int(parser.get('camera','stream_write_length'))
    except ConfigParser.Error as e:
        print(e)

def cleanup():
#    time.sleep(100)
    global cmd_socket1
    global cmd_socket2
    global sockfd1
    global sockfd2
    global stream_socket1
    global stream_socket1
    print("cmd_socket1: %s" % cmd_socket1)
    if sockfd1 is not None:
        print("closing down cmd_socket1")
        cmd_socket1.shutdown(socket.SHUT_RDWR)
        cmd_socket1.close()
#    cmd_socket2.shutdown(socket.SHUT_RDWR)
    if sockfd2 is not None:
        print("closing down cmd_socket2")
        cmd_socket2.shutdown(socket.SHUT_RDWR)
        cmd_socket2.close()
    # stream_socket1.shutdown(socket.SHUT_RDWR)
    # stream_socket1.close()
    # stream_socket2.shutdown(socket.SHUT_RDWR)
    # stream_socket2.close()
    print("cleaned up")

def sendCmd(cmd):
#    global cmd_socket1
#    global cmd_socket2
    global sockfd1
#    global addr1
    global sockfd2
#    global addr2
    try:
        if sockfd1 is not None:
            sockfd1.sendall(cmd)
            print("sent command: %s to socket1" % cmd)
        if sockfd2 is not None:
            sockfd2.sendall(cmd)
            print("send command: %s to socket2" % cmd)
        # if cmd_socket2 is not None:
        #     cmd_socket2.send(cmd)
        #     print("sent command: %s to socket2" % cmd)
    except Exception as e:
        traceback.print_exc()

class cmdNetworkThread(threading.Thread):
    def __init__(self, threadID, name, cl1, cl2, lport1, lport2):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.client1 = cl1
        self.client2 = cl2
        self.cmd_port1 = lport1
        self.cmd_port2 = lport2
        self.socket1_connect = False
        self.socket2_connect = False
        self.ip = '0.0.0.0' # listen all interfaces

    def run(self):
        global cmd_socket1
        global cmd_socket2
        global sockfd1
#        global addr1
        global sockfd2
#        global addr2
#        try:
        while True:
            if not self.socket1_connect:
                try:
                    cmd_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    cmd_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#                    cmd_socket1.setblocking(0)
                    cmd_socket1.settimeout(0.1)
                    cmd_socket1.bind( (self.ip, self.cmd_port1) )
                    cmd_socket1.listen(0)
                    sockfd1, addr1 = cmd_socket1.accept()
                    cmd_socket1.setblocking(True)
                    self.socket1_connect = True
                    print('cmd_socket1: %s, %s' % (sockfd1, addr1))
                except socket.error as so:
                    if so != None and so.errno == errno.ECONNREFUSED:
                        time.sleep(0.01)
                        pass
#            print('self.socket2_connect: %s' % self.socket2_connect)
            if not self.socket2_connect:
                try:
                    cmd_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    cmd_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#                    cmd_socket2.setblocking(0)
                    cmd_socket2.settimeout(0.1)
                    cmd_socket2.bind( (self.ip, self.cmd_port2) )
                    cmd_socket2.listen(0)
                    sockfd2, addr2 = cmd_socket2.accept()
                    cmd_socket2.setblocking(True)
                    print("cmd_socket2: %s, %s" % (sockfd2, addr2))
                    self.socket2_connect = True
                except socket.error as sk:
                    if sk.errno == errno.ECONNREFUSED:
                        time.sleep(0.01)
                        pass
                    # else:
                    #     print('socket.error: %s' % sk)
                    #     traceback.print_exc(file=sys.stdout)
            if self.socket1_connect and self.socket2_connect:
                break
        # except socket.error as e:
        #     if e.errno == errno.ECONNREFUSED:
        #         #                    print('connect error: %s' % e)
        #         time.sleep(0.1)
        #         pass
        #     else:
        #         print('socket error: %s' % e)                    
        #         traceback.print_exc(file=sys.stdout)

def showVideo(streamSocket, name, queue, tlock):
    try:
        print("streamSocket: %s" % streamSocket)
        while True:
            # unpack the python struck as long integer, litte endian
            image_len = struct.unpack('<L',streamSocket.read(4))[0]
            if not image_len:
                break
            image_stream = io.BytesIO()
            image_stream.write(streamSocket.read(image_len))
            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)
            image = Image.open(image_stream)
            # convert PIL to opencv
            imgnp = np.array(image)
            imgcv = imgnp[:, :, ::-1].copy()
            queue.put(imgcv)

            # now that we have our opencv frame, let's
            # do some processing on it
#            if len(imgcv) > 0:
#                gray = cv2.cvtColor(imgcv, cv2.COLOR_BGR2GRAY)
#                edges = cv2.GaussianBlur(gray, (3,3), 0)
#                edges = cv2.Canny(edges,100,200)
                # print imgcv.shape
                # print edges.shape
                # print gray.shape
                # print('\n\n')
#                imgedges = imgcv.copy()
#                imgedges[edges != 0] = (255,255,0) # yellow
#                tlock.acquire()
#                cv2.imshow(name, imgedges)
#                tlock.release()
#                cv2.waitKey(1)
    except cv2.error as e:
        traceback.print_exc()

class streamNetworkThread(threading.Thread):
    def __init__(self, ThreadID, name, stream_port, queue, tlock):
        threading.Thread.__init__(self)
        self.stream_port = stream_port
        self.name = name
        self.socket1_connect = False
        self.socket2_conenct = False
        self.ip = '0.0.0.0' # listen all interfaces
        self.tlock = tlock
        self.queue = queue

    def run(self):
#        global stream_port
        global stream_socket
        global streamThread1
        try:
            while True:
                if not self.socket1_connect:
                    print "connecting to stream socket: %s, %d" % (self.ip, self.stream_port)
                    stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    stream_socket.bind((self.ip, self.stream_port))
                    stream_socket.listen(0)
                    streamConnection = stream_socket.accept()[0].makefile('rb')
                    sv = threading.Thread(target=showVideo, args=(streamConnection, self.name, self.queue, self.tlock))
                    sv.daemon = True
                    sv.start()
                    print("streamConnection: %s" % streamConnection)
                    self.socket1_connect = True
#                print("stream socket connecting break")
                time.sleep(0.01)
                break
        except socket.error as e:
            if e != None and e.errno == errno. ECONNREFUSED:
                print('stream socket connect error: %s' % e)
                time.sleep(0.1)
                pass

def main():
    global stream_socket1
    global stream_socket2
#    old_settings = termios.tcgetattr(sys.stdin)
    try:
        queue1 = Queue.Queue(3)
        queue2 = Queue.Queue(3)
        tlock = threading.Lock()
        readConfig()
        time.sleep(0.001)
        cmdThread = cmdNetworkThread(1, "cmd thread", client1, client2, cmd_port1, cmd_port2)
        cmdThread.daemon = True
        cmdThread.start()
        streamThread1 = streamNetworkThread(1, 'Stream from ' + client1, stream_port1, queue1, tlock)
        streamThread1.daemon = True
        streamThread1.start()
        streamThread2 = streamNetworkThread(2, 'Stream from ' + client2, stream_port2, queue2, tlock)
        streamThread2.daemon = True
        streamThread2.start()
        time.sleep(0.1)
        name = 'NH Video Collect'
#        cv2.namedWindow(name, cv2.CV_WINDOW_AUTOSIZE)
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
#        cv2.namedWindow(name, cv2.WINDOW_NORMAL | cv2.WINDOW_OPENGL)
        time.sleep(0.1)
 #       tty.setcbreak(sys.stdin.fileno())
        while True:
            im1 = queue1.get()
#            print "got pic1"
            im2 = queue2.get()
#            print "got pic2"
#            cv2.imshow(name, im1)
            both = np.hstack( (im1,im2) )
            cv2.imshow(name, both)
            cv2.waitKey(1)
#            time.sleep(0.001)
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                key = sys.stdin.read(1)
                if key == "e":
#                    print("key == e")
                    sendCmd("e")
                    time.sleep(0.5) # give clients time to cleanup before killing connections
#                print("key == %c" % key)
                    break
                elif key == "r":
#                    print("key == r")
                    sendCmd("r")
#                print("key == $c\n" % key)
                elif key == "s":
#                    print("key == s")
                    sendCmd("s")

#             key = raw_input('input command: ').decode(sys.stdin.encoding)
#             if key == "e":
#                 print("key == e")
#                 sendCmd("e")
#                 time.sleep(0.5) # give clients time to cleanup before killing connections
# #                print("key == %c" % key)
#                 break
#             elif key == "r":
#                 print("key == r")
#                 sendCmd("r")
# #                print("key == $c\n" % key)
#             elif key == "s":
#                 print("key == s")
#                 sendCmd("s")
#    except Exception, e:
    except:
#        cleanup()
        traceback.print_exc()
        print('Exception caught, exiting cameraStreamCollect')
    finally:
        cleanup()
#        traceback.print_exc()
        print('finally exiting')
#        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        cv2.destroyAllWindows()
        sys.exit(0)
    
if __name__ == "__main__":
    main()
