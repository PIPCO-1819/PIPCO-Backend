from datetime import date

import cv2
import time
from DataStorage import PipcoDaten
import CyclicList
from threading import Thread
from MailClient import MailClient

class ImageProcessing(Thread):

    m_dataBase = PipcoDaten.get_instance()
    m_exit = False
    m_changed = False
    m_images = CyclicList.cyclicList(25)
    m_lastMotionTime = None

    def __init__(self, debug):
        self.__m_run = True
        self.__m_debug = debug
        self.__m_mailclient = MailClient(ImageProcessing.m_dataBase)
        if debug:
            self.m_stream = "videosamples/sample2.mkv"
        else:
            self.m_stream = ImageProcessing.m_dataBase.get_settings().streamaddress

        print("init")
        super(ImageProcessing, self).__init__()

    def stop(self):
        self.__m_run = False

#   Aeussere Schleife um run mit neuen Parametern auszufuehren
    def run(self):
        while self.__m_run:
            self.m_changed = False
            self.run_imgprocessing()

            if self.m_exit:
                self.m_exit = False
                break

#   Eigentliche Bildverarbeitung
    def run_imgprocessing(self):
        cap = cv2.VideoCapture(self.m_stream)
        print("Enter Loop")
        while self.__m_run:
            ret, frame = cap.read()
        #   (read) If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file),
        #   the methods return false and the functions return NULL pointer.
            if ret:
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                motion = self.check_image(gray_image)

                if len(motion):
                    cv2.drawContours(frame, motion, -1, (0,255,0), 3)

                ret2, jpg = cv2.imencode('.jpg', frame)
                self.m_dataBase.set_image(jpg)

            elif self.__m_debug:
                # if video ist playing, reset video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            cv2.waitKey(40)

        #   verlaesst Funktion um run mit den neuen Parametern aufzurufen
            if self.m_changed:
                return

        #    print(datetime.datetime.now())

    def check_image(self,image):
        old_image = self.m_images.get_last_image()
        new_image = cv2.GaussianBlur(image,(21,21),0)
        self.push_front(new_image)

        if old_image is None:
            return []

        delta_frame = cv2.absdiff(new_image,old_image)
        thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

#        ret2, jpg = cv2.imencode('.jpg', thresh_frame)
 #       self.m_dataBase.set_image(jpg)

        (_, cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts):
            if self.compare_time():
                self.notify()
            self.m_lastMotionTime = int(round(time.time()*1000))
            return cnts

        return []


    def notify(self):
        print("Motion detected")
        #self.__m_mailclient.notify_users()


    def set_stream(self, stream):
        self.m_stream = stream
        self.m_changed = True

    def push_front(self, image):
        self.m_images.push_front(image)

#   dauer von 5 Sekunden abgelaufen
    def compare_time(self):
        now = int(round(time.time()*1000))

        if self.m_lastMotionTime is not None:
            # vergleich ob 5 Sekunden abgelaufen sind
            delta = now-self.m_lastMotionTime
            return (now-self.m_lastMotionTime) >= 1000*7

        return True





