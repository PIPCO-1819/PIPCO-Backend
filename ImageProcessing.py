import cv2
import DataStorage
from threading import Thread


class ImageProcessing(Thread):
    m_dataBase = DataStorage.PipcoDaten.getInstance()
    m_exit = False
    m_changed = False

    def __init__(self, debug):
        self.__m_debug = debug
        if debug:
            self.m_stream = "videosamples/sample2.mkv"
        else:
            self.m_stream = "http://192.168.0.35/cgi-bin/videostream.cgi?user=admin&pwd=admin"

        print("init")
        super(ImageProcessing, self).__init__()

#   Äußere Schleife um run mit neuen Parametern auszuführen

    def run(self):
        while(True):
            self.m_changed = False
            self.run_imgprocessing()

            if self.m_exit:
                self.m_exit = False
                break

#   Eigentliche Bildverarbeitung
    def run_imgprocessing(self):
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
                    self.notify(self.m_dataBase.getMails())

                ret2, jpg = cv2.imencode('.jpg', frame)
                self.m_dataBase.set_image(jpg)

            elif self.__m_debug:
                #if video ist playing, reset video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            cv2.waitKey(40)

        #   verlässt Funktion um run mit den neuen Parametern aufzurufen
            if self.m_changed:
                return

        #    print(datetime.datetime.now())

    def checkImage(self,image):
        return False

    def notify(self, mails):
        for mail in mails:
            return

    def setStream(self, stream):
        self.m_stream = stream
        self.m_changed = True



