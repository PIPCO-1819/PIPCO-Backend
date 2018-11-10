import cv2

#   cap = cv2.VideoCapture("57962.jpg")
cap = cv2.VideoCapture("http://192.168.0.35/cgi-bin/videostream.cgi?user=admin&pwd=admin")

while(True):
    ret, frame = cap.read()
#   (read) If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file),
#   the methods return false and the functions return NULL pointer.
    if(ret):
        cv2.imshow('Video',frame)
    cv2.waitKey(40)
#    print(datetime.datetime.now())
