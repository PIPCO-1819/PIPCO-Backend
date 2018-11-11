import cv2
import DataStorage

class ImageProcessing:
    m_dataBase = DataStorage.PipcoDaten.getInstance(DataStorage.PipcoDaten)
#    m_stream = "http://192.168.0.35/cgi-bin/videostream.cgi?user=admin&pwd=admin"
    m_stream = "http://eckardtscholz.viewnetcam.com/nphMotionJpeg?Resolution=640x480"
    m_exit = False
    m_changed = False

    def __init__(self):
        print("init")

#   Äußere Schleife um run mit neuen Parametern auszuführen
    def run_manager(self):
        while True:
            self.m_changed = False
            self.run()

            if self.m_exit:
                self.m_exit = False
                break

#   Eigentliche Bildverarbeitung
    def run(self):
        cap = cv2.VideoCapture(self.m_stream)
        print("Enter Loop")

        while True:
            ret, frame = cap.read()
        #   (read) If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file),
        #   the methods return false and the functions return NULL pointer.
            if ret:
                motion = self.checkImage(frame)
                self.m_dataBase.addImage(frame)

                if motion:
                    self.notify(ImageProcessing.m_dataBase.getMails())

                cv2.imshow('Video',frame)
            cv2.waitKey(40)

        #   verlässt Funktion um run mit den neuen Parametern aufzurufen
            if self.m_changed:
                return;

        #    print(datetime.datetime.now())

    def checkImage(self,image):
        return False

    def notify(self,mails):
        for mail in mails:
            return

    def setStream(self,stream):
        self.m_stream = stream
        self.m_changed = True


ImageProcessing().run_manager()


