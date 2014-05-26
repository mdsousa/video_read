import cv2
import threading
import curses
import atexit
import traceback
import time

key = 'x'

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
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
#    print 'cleaned up'
#    exit(0)


class keyInput (threading.Thread):
#    global key
#    global stdscr
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        print '6'

    def run(self):
#        try:
            curses.nl()
#            print 'waiting for key'
#            stdscr.addstr("waiting for key\n")
#            stdscr.refresh()
            global key
            stdscr.nodelay(1)
            while True:
#                stdscr.addstr("waiting for key\n\n")
#                stdscr.refresh()
#                k = raw_input()
                try:
                    k = stdscr.getch()
#                    stdscr.addstr("key retrieved\n\n")
                # if k == 'Escape':
                #     print 'Escape'
                # elif k == 's':
                #     print 's'
                # elif k == ord('e'):
                    if k == ord('e'):
                        stdscr.addstr("e pressed\n")
#                        stdscr.addstr('k == {}\n', str(unichr(k)))
#                        stdscr.addstr("k == \n")
                        stdscr.refresh()
                        key = 'e'
                        stdscr.addch(key)
                        stdscr.refresh()
                        cleanup()
                        break
                    elif k == ord('r'):
                        stdscr.addstr("r pressed\n")
                        stdscr.refresh()
                    elif k == ord('s'):
                        stdscr.addstr("s pressed\n")
                        stdscr.refresh()
                except curses.ERR:
                    pass
#               time.sleep(1000)
#        except Exception, e:
#            print 'Exception in thread: %s' % e.strerror
#                    key = 'e'
#                finally:
#                    break
#            cleanup()

def main():
    global key
    try:
    #    global stdsrcr
        print '1'
        atexit.register(cleanup)
        print '2'
        setupCurses()
#        stdscr.addstr("3")
#        addch('\n')
#        stdscr.refresh()
        print '3'
        thread1 = keyInput(1, "thread-1", 1)
#        stdscr.addstr("4")
#        addch('\n')
#        stdscr.refresh()
        print '4'
        thread1.start()
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
