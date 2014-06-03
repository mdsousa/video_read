import cv2
import threading
import curses
import atexit
import traceback
import time
import socket
import errno
import ConfigParser # read config file


key = 'x'
thread1 = None
cmdThread = None

#
# For each client sending video, need a socket for sending cmds and one for retrieving data
#
client1 = None
client2 = None
listen_socket1 = None
listen_socket2 = None
stream_socket1 = None
stream_socket2 = None
listen_port = None
stream_port = None
stream_write_length = None

def readConfig():
    global client1
    global client2
    global listen_socket1
    global listen_socket2
    global stream_socket1
    global stream_socket1
    global listen_port
    global stream_port
    global stream_write_length
    try:
        parser = ConfigParser.ConfigParser()
        parser.read('config_pi_server.cfg')
        client1 = parser.get('configuration','client1')
        print('client1: %s' % client1)
        client2 = parser.get('configuration','client2')
        print('client2: %s' % client2)
        listen_port = int(parser.get('configuration','listen_port'))
        stream_port = int(parser.get('configuration','stream_port'))
        stream_write_length = int(parser.get('camera','stream_write_length'))
    except ConfigParser.Error as e:
        print(e)

def setupCurses():
    try:
        global stdscr
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
#        curses.echo()
#        k = stdscr.getch()
#        time.sleep(200)
    except:
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()
        print(curses.ERR)
    # finally:
    #     stdscr.keypad(0)
    #     curses.echo()
    #     curses.nocbreak()
    #     curses.endwin()
    #     print 'finally'
    #    traceback.print_exc()

def cleanup():
#    time.sleep(100)
    global listen_socket1
    global listen_socket2
    global stream_socket1
    global stream_socket1
#    listen_socket1.shutdown(socket.SHUT_RDWR)
    if listen_socket1 is not None:
        listen_socket1.close()
#    listen_socket2.shutdown(socket.SHUT_RDWR)
    if listen_socket2 is not None:
        listen_socket2.close()
    # stream_socket1.shutdown(socket.SHUT_RDWR)
    # stream_socket1.close()
    # stream_socket2.shutdown(socket.SHUT_RDWR)
    # stream_socket2.close()
#    time.sleep(100)
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
#    print 'cleaned up'
#    exit(0)


class keyInput (threading.Thread):
#    global key
#    global stdscr
    global cmdThread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        print '6'

    def run(self):
#        try:
#            curses.nl()
#            print 'waiting for key'
#            stdscr.addstr("waiting for key\n")
#            stdscr.refresh()
            global key
            stdscr.nodelay(1)
            while True:
                try:
                    k = stdscr.getch()
#                    stdscr.addstr("key retrieved\n\n")
                    if k == ord('e'):
                        stdscr.refresh()
                        stdscr.addstr("e pressed\n")
                        stdscr.refresh()
                        key = 'e'
#                        stdscr.addch(key)
#                        stdscr.refresh()
                        cleanup()
                        break
                    elif k == ord('r'):
                        key = 'r'
                        stdscr.refresh()
                        stdscr.addstr("r pressed\n")
                        stdscr.refresh()
                    elif k == ord('s'):
                        stdscr.refresh()
                        key = 's'
                        stdscr.refresh()
                        stdscr.addstr("s pressed\n")
                        stdscr.refresh()
                except curses.ERR:
                    stdscr.addstr("curses.ERR\n")
                    stdscr.refresh()
                    pass
#               time.sleep(1000)
#        except Exception, e:
#            print 'Exception in thread: %s' % e.strerror
#                    key = 'e'
#                finally:
#                    break
#            cleanup()

def sendCmd(cmd):
    global listen_socket1
    global listen_socket2
    try:
        print("sending command: %s" % cmd)
        listen_socket1.send(cmd)
        listen_socket2.send(cmd)
    except Exception as e:
        print 'Exception in sendCmd: %s' % e.strerror


class cmdNetworkThread(threading.Thread):
    global client1
    global client2
    global listen_socket1
    global listen_socket2
    global listen_port
    def __init__(self, threadID, name, cl1, cl2, lport):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.client1 = cl1
        self.client2 = cl2
        self.listen_port = lport

    def run(self):
        print(client1)
        print(client2)
        while True:
            try:
                listen_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                listen_socket1.connect( (self.client1, self.listen_port) )
#                listen_socket1.bind( (self.server, self.listen_port) )
                listen_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                listen_socket2.connect( (self.client2, self.listen_port) )
#                listen_socket2.bind( (self.server, self.listen_port) )
                time.sleep(100)
                break
            except socket.error as e:
                if e.errno == errno.ECONNREFUSED:
                    pass



def main():
    global key
    global thread1
    global cmdThread
    try:
    #    global stdsrcr
        readConfig()
        print '1'
        atexit.register(cleanup)
        print '2'
        setupCurses()
        print '3'
        thread1 = keyInput(1, "thread-1", 1)
        cmdThread = cmdNetworkThread(1, "cmd thread", client1, client2, listen_port)
        print '4'
        thread1.start()
        cmdThread.start()
        print '5'
    #    thread.start_new_thread(keyInput, ())
        while True:
#            print('key == %s' % key)
            if key == 'e' or key == ord('e'):
#            if key == 'e':
                cleanup()
                print('key == %s' % key)
                print('exiting\n')
                break
            elif key == 'r' or key == ord('r'):
                sendCmd('r')
            elif key == 's' or key == ord('s'):
                sendCmd('s')
    #            exit(0)
    #        time.sleep(100)
#    except Exception, e:
    except:
        cleanup()
        traceback.print_exc()
        print 'Exception caught, exiting threadTest'
    finally:
        cleanup()
#        traceback.print_exc()
        print 'exiting'
        exit(0)
    
if __name__ == "__main__":
    main()
