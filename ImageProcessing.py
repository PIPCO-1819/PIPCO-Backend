import cv2
import time
import numpy as np
import CyclicList
from DataStorage import PipcoDaten, THUMBNAIL_PATH, RECORDINGS_PATH
from threading import Thread
from MailClient import MailClient

FPS = 25
MOTION_SEC = 7

class ImageProcessing(Thread):

    m_dataBase = PipcoDaten.get_instance()
    m_images = CyclicList.cyclicList(20)
    m_lastMotionTime = 0

    def __init__(self, debug):
        self.__m_run = True
        self.__m_debug = debug
        self.__m_mailclient = MailClient(ImageProcessing.m_dataBase)
        self.m_sensitivity = 0.5
        if debug:
            self.m_stream = "videosamples/sample2.mkv"
            self.m_dataBase.change_settings(None,None,None,self.m_stream)
        else:
            self.m_stream = ImageProcessing.m_dataBase.get_settings().streamaddress

        print("init")
        super(ImageProcessing, self).__init__()

    def stop(self):
        self.__m_run = False

#   Aeussere Schleife um run mit neuen Parametern auszufuehren
    def run(self):
        while self.__m_run:
            self.m_stream_changed = False
            self.run_imgprocessing()


#   Eigentliche Bildverarbeitung
    def run_imgprocessing(self):
        cap = cv2.VideoCapture(self.m_stream)
        update_counter = 0
        print("Enter Loop")
        last = time.time()
        out = None

        while self.__m_run:
            ret, frame = cap.read()
        #   (read) If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file),
        #   the methods return false and the functions return NULL pointer.
            if ret:
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                motion = self.check_image(gray_image)

                if self.compare_time(MOTION_SEC):
                    if len(motion):
                        self.notify()
                        idx = self.m_dataBase.add_log()
                        self.save_thumbnail(frame, idx)

                        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        heigth = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

                        ouput_str = RECORDINGS_PATH+str(idx)+".avi"
                        out = cv2.VideoWriter(ouput_str, cv2.VideoWriter_fourcc(*'MJPG'), 20, (int(width), int(heigth)))
                        print("Videocapture start")
                    else:
                        if out is not None:
                            print("Videocapture end")
                            out = None

                if len(motion):
                    cv2.drawContours(frame, motion, -1, (0, 255, 0), 3)
                    self.m_lastMotionTime = int(round(time.time() * 1000))

                if out is not None:
                    out.write(frame)
                ret2, jpg = cv2.imencode('.jpg', frame)
                self.m_dataBase.set_image(jpg)
                now = time.time()
                print(now - last)
                last = now

            elif self.__m_debug:
                # if video ist playing, reset video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # update settings every second
            update_counter += 1
            if update_counter >= FPS:
                update_counter = 0
                self.update_settings()

        #   verlaesst Funktion um run mit den neuen Parametern aufzurufen
            if self.m_stream_changed:
                return

        #    print(datetime.datetime.now())

    def check_image(self,image):
        #old_image = ImageProcessing.m_images.get_last_image()
        new_image = cv2.GaussianBlur(image,(21,21),0)
        self.push_front(new_image)
        old_image = self.get_median()

        if old_image is None:
            return []

        delta_frame = cv2.absdiff(new_image,old_image)
        thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.erode(thresh_frame, None, iterations=int(10*(1-self.m_sensitivity)))
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        (_, cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts):
            return cnts

        return []


    def get_median(self):
        if ImageProcessing.m_images.get_list():
            image_stack = np.concatenate([im[..., None] for im in ImageProcessing.m_images.get_list()], axis=2)
            median_array = np.median(image_stack, axis=2)
            return np.asarray(median_array, np.uint8)

    def notify(self):
        print("Motion detected")
        if not self.__m_debug:
            self.__m_mailclient.notify_users()

    def update_settings(self):
        settings = self.m_dataBase.get_settings()
        if self.m_stream != settings.streamaddress:
            self.m_stream_changed = True
            self.m_stream = settings.streamaddress
        self.m_sensitivity = settings.sensitivity
        self.m_contrast = settings.contrast
        self.m_brightness = settings.brightness

    def push_front(self, image):
        self.m_images.push_front(image)

#   dauer von x Sekunden abgelaufen
    def compare_time(self, val):
        now = int(round(time.time()*1000))

        if self.m_lastMotionTime is not None:
            # vergleich ob x Sekunden abgelaufen sind
            delta = now-self.m_lastMotionTime
            return (now-self.m_lastMotionTime) >= 1000*val

        return True

    def save_thumbnail(self, image, id):
        small = cv2.resize(image, (0, 0), fx=0.2, fy=0.2)
        cv2.imwrite(THUMBNAIL_PATH + str(id) + '.jpg', small)



