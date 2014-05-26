import thread
import time

#img = LoadImage("/home/mike/altera/12.1/nios2eds/documents/html_content/altera_banner.jpg")
#img = cv2.imread("/home/mike/altera/12.1/nios2eds/documents/html_content/altera_banner.jpg")
#NamedWindow("opencv")
#cv2.namedWindow('opencv', cv2.WINDOW_NORMAL)
#cv2.imshow('opencv',img)
#ShowImage("opencv",img)
def testWaitKey():
    global keyPress
    while True:
        k=cv2.waitKey(0) & 0xFF
        if k == 27:
            keyPress = k
        else if k == 10:
            cv2.destroyAllWindows()

while True:
    print keyPress
    time.sleep(2000)

testWaitKey.start()
