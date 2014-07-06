import os
import datetime
import cv2
import time
import traceback
import sys
import Queue

def saveCollection(location, image_stream_left_queue, image_stream_right_queue, gps_queue, doneRecordingQueue):
    doneRecording = False
    try:
        now = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S%f')[:-3] # want to milliseconds - helps with generating unique filenames
        pathl = location+'/'+now+'/'+'left'
        pathr = location+'/'+now+'/'+'right'
        pathg = location+'/'+now+'/'+'gps'
        print("saveCollection starting")
        if( not (os.path.exists(location+'/'+ now+'/'+'left') and os.path.exists(location+'/'+now+'/'+'right')) ):
            print('leftDir = %s' % pathl)
            print('rightDir = %s' % pathr)
            print('gpsDir = %s' % pathg)
            os.makedirs(pathl, 0777)
            os.makedirs(pathr, 0777)
            os.makedirs(pathg, 0777)
            inc = 1
            while not doneRecording:
                time.sleep(0.01)
                filename = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S%f')[:-3]
                iml = image_stream_left_queue.get()
                imr = image_stream_right_queue.get()
                left = pathl+'/'+filename+'_'+str(inc)+'_left.jpg'
                right = pathr+'/'+filename+'_'+str(inc)+'_right.jpg'
                cv2.imwrite(left, iml)
                cv2.imwrite(right, imr)
                gps = pathg+'/'+filename+'_'+str(inc)+'.txt'
                g = open(gps, 'w')
                gps = gps_queue.get()
                try:
                    g.write(gps)
                except TypeError as te:
                    g.write("No GPS Data")
                    pass
                g.close()
                try:
                    doneRecording = doneRecordingQueue.get(False, 0.01)
                    print("%d doneRecording: %s" % (inc, doneRecording))
                    # stopRecording = doneRecordingQueue.get(False, 0.001)
                    # print("%d stopRecording: %s" % (inc, stopRecording))
                    # if( inc%100 == 0 ):
                    #     print("%d stopRecording = %s" % (inc,stopRecording))
                    # if(stopRecording == True):
                    #     print("Request to stop recording received")
                    #     doneRecording = True
                except Queue.Empty as qe:
#                    print("%d Queue empty" % inc)
                    pass
                inc += 1
            print("saveCollection closing")
    except os.error as oe:
        traceback.print_exc()
        sys.exit(1)

def main():
    print("Save Collection")

if __name__ == "__main__":
    main()

