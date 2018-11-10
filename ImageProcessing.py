import cv2
import DataStorage

class ImageProcessing:
    m_dataBase = DataStorage.PipcoDaten.getInstance()
    m_stream = "http://192.168.0.35/cgi-bin/videostream.cgi?user=admin&pwd=admin"
    m_exit = False
    m_changed = False

#   Äußere Schleife um run mit neuen Parametern auszuführen
    @staticmethod
    def run_manager(self):
        while(True):
            ImageProcessing.m_changed = False
            ImageProcessing.run()

            if ImageProcessing.m_exit:
                ImageProcessing.m_exit = False
                break

#   Eigentliche Bildverarbeitung
    def run(self):
        cap = cv2.VideoCapture(ImageProcessing.m_stream)

        while(True):
            ret, frame = cap.read()
        #   (read) If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file),
        #   the methods return false and the functions return NULL pointer.
            if ret:
                motion = ImageProcessing.checkImage(frame)
                ImageProcessing.m_dataBase.addImage(frame)

                if motion:
                    ImageProcessing.notify(ImageProcessing.m_dataBase.getMails())

                cv2.imshow('Video',frame)
            cv2.waitKey(40)

        #   verlässt Funktion um run mit den neuen Parametern aufzurufen
            if ImageProcessing.m_changed:
                return;

        #    print(datetime.datetime.now())

    def checkImage(self,image):
        if image:
            return True
        else:
            return False

    def notify(self,mails):
        for mail in mails:
            return

    def setStream(self,stream):
        ImageProcessing.m_stream = stream
        ImageProcessing.m_changed = True



process = ImageProcessing()

process.run_manager()


