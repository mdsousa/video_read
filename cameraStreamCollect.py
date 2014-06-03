import socket
import threading
import ConfigParser # read config file
import traceback
import signal
import sys
import errno

import time
import Queue
import cv2


#
# For each client sending video, need a socket for sending cmds and one for retrieving data
#
client1 = None
client2 = None
cmd_socket1 = None
cmd_socket2 = None
cmd_port = None
stream_port = None
stream_write_length = None
stream_socket1 = None
stream_socket2 = None
sockfd1 = None
addr1 = None

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
    global cmd_port
    global stream_port
    global stream_write_length
    try:
        parser = ConfigParser.ConfigParser()
        parser.read('config_pi_server.cfg')
        client1 = parser.get('configuration','client1')
#        print('client1: %s' % client1)
        client2 = parser.get('configuration','client2')
#        print('client2: %s' % client2)
        cmd_port = int(parser.get('configuration','cmd_port'))
        stream_port = int(parser.get('configuration','stream_port'))
        stream_write_length = int(parser.get('camera','stream_write_length'))
    except ConfigParser.Error as e:
        print(e)

def cleanup():
#    time.sleep(100)
    global cmd_socket1
    global cmd_socket2
    global stream_socket1
    global stream_socket1
    print("cmd_socket1: %s" % cmd_socket1)
    if cmd_socket1 is not None:
        print("closing down cmd_socket1")
        cmd_socket1.shutdown(socket.SHUT_RDWR)
        cmd_socket1.close()
#    cmd_socket2.shutdown(socket.SHUT_RDWR)
    if cmd_socket2 is not None:
        cmd_socket2.close()
    # stream_socket1.shutdown(socket.SHUT_RDWR)
    # stream_socket1.close()
    # stream_socket2.shutdown(socket.SHUT_RDWR)
    # stream_socket2.close()
    print("cleaned up")

# def get_user_input(kq):
#     k = input('input command: ')
#     kq.put(k)

def sendCmd(cmd):
    global cmd_socket1
    global cmd_socket2
    global sockfd1
    global addr1
    try:
        if sockfd1 is not None:
            sockfd1.sendall(cmd)
            print("sent command: %s to socket1" % cmd)
        if cmd_socket2 is not None:
            cmd_socket2.send(cmd)
            print("sent command: %s to socket2" % cmd)
    except Exception as e:
        traceback.print_exc()

class cmdNetworkThread(threading.Thread):
#    global cmd_socket1_conn
#    global cmd_port
    def __init__(self, threadID, name, cl1, cl2, lport):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.client1 = cl1
        self.client2 = cl2
        self.cmd_port = lport
        self.socket1_connect = False
        self.socket2_connect = False
        self.ip = '0.0.0.0'

    def run(self):
        global cmd_socket1
        global cmd_socket2
        global sockfd1
        global addr1
        while True:
            try:
                if not self.socket1_connect:
                    cmd_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("cmd_socket1 creation: %s" % cmd_socket1)
                    cmd_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    cmd_socket1.bind( (self.ip, self.cmd_port) )
                    print("cmd_socket1 bind: %s" % cmd_socket1)
                    cmd_socket1.listen(0)
                    print("cmd_socket1 listening: %s" % cmd_socket1)
                    sockfd1, addr1 = cmd_socket1.accept()
                    print("cmd_socket1 accept: %s, %s" % (sockfd1,addr1))
                    self.socket1_connect = True
#                    print('socket1 connection made')
#                cmd_socket1.bind( (self.server, self.cmd_port) )
                # if not self.socket2_connect:
                #     cmd_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #     cmd_socket2.connect( (self.client2, self.cmd_port) )
                #     self.socket2_connect = True
                #     print('client2: %s' % client2)
#                cmd_socket2.bind( (self.server, self.cmd_port) )
                time.sleep(0.01)
                print("socket connecting loop breaking")
#                output_sockets(cmd_socket1_conn)
                break
            except socket.error as e:
                if e.errno == errno.ECONNREFUSED:
                    print('connect error: %s' % e)
                    time.sleep(0.1)
                    pass

def output_sockets(conn):
    global cmd_socket1_conn
    print("conn: %s" % conn)

def main():
#    global key
    try:
    #    global stdsrcr
        readConfig()
#        print('1')
        cmdThread = cmdNetworkThread(1, "cmd thread", client1, client2, cmd_port)
        cmdThread.daemon = True
#        print('2')
        cmdThread.start()
#        print('3')
        time.sleep(0.5)
    #    thread.start_new_thread(keyInput, ())
        while True:
#            k = keyQueue.get()
#            print('getting input')
            key = raw_input('input command: ').decode(sys.stdin.encoding)
            if key == "e":
                print("key == e")
                sendCmd("e")
#                print("key == %c" % key)
                break
            elif key == "r":
                print("key == r")
                sendCmd("r")
#                print("key == $c\n" % key)
            elif key == "s":
                print("key == s")
                sendCmd("s")
#                print("key == %c" % key)
#            print('key == %s' % key)
#             if key == 'e' or key == ord('e'):
# #            if key == 'e':
# #                cleanup()
#             elif key == 'r' or key == ord('r'):
#                 sendCmd('r')
#             elif key == 's' or key == ord('s'):
#                sendCmd('s')
    #            exit(0)
    #        time.sleep(100)
#    except Exception, e:
    except:
#        cleanup()
        traceback.print_exc()
        print('Exception caught, exiting cameraStreamCollect')
    finally:
        cleanup()
#        traceback.print_exc()
        print('finally exiting')
        sys.exit(0)
    
if __name__ == "__main__":
    main()
