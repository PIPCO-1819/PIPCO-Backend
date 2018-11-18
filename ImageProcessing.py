import cv2
from DataStorage import PipcoDaten
import CyclicList
from threading import Thread


class ImageProcessing(Thread):

    m_dataBase = PipcoDaten.get_instance()
    m_exit = False
    m_changed = False
    m_images = CyclicList.cyclicList(25)

    def __init__(self, debug):
        self.__m_debug = debug
        if debug:
            self.m_stream = "videosamples/sample2.mkv"
        else:
            self.m_stream = ImageProcessing.m_dataBase.get_settings().streamaddress

        print("init")
        super(ImageProcessing, self).__init__()

#   Äußere Schleife um run mit neuen Parametern auszuführen
    def run(self):
        while True:
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
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                motion = self.check_image(gray_image)
                self.push_front(gray_image)

                if motion:
                    self.notify(self.m_dataBase.get_mails())

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

    def check_image(self,image):
        old_image = self.m_images.get_last_image()
        image = cv2.GaussianBlur(image, 21, 0)

        if old_image is None:
            old_image = image

        delta_frame = cv2.absdiff(self.m_images.get_last_image(),image)

        thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        (_, cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts):
            return True

        return False

    def notify(self, mails):
        for mail in mails:
            return False

    def set_stream(self, stream):
        self.m_stream = stream
        self.m_changed = True

    def push_front(self, image):
        self.m_images.push_front(image)
        self.m_dataBase.set_image(image)




