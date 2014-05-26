import cv2
import threading
import atexit
import traceback
import time

key = None

def cleanup():
    print 'cleaned up'


class cameraInput(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        print '6'

    def run(self):
        try:
            print 'waiting for camera'
#            while True:
                # k = stdscr.getch()
                # if k == 'Escape':
                #     print 'Escape'
                # elif k == 's':
                #     print 's'
                # elif k == 'e':
                #     key = k
#               time.sleep(1000)
        except Exception, e:
            print 'Exception in thread: %s' % e.strerror

def main():
    try:
    #    global stdsrcr
        print '1'
        atexit.register(cleanup)
        print '2'
#        print '3'
        thread1 = cameraInput(1, "thread-1", 1)
        print '4'
        thread1.start()
        print '5'
    #    thread.start_new_thread(keyInput, ())
#        while True:
    except Exception, e:
        print 'Exception caught, exiting threadTest: %s' % e.strerror
    finally:
        print 'exiting'
        exit(0)
    
if __name__ == "__main__":
    main()
