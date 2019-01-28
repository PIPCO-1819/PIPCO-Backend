import cv2
import time
import numpy as np
from DataStorage import PipcoDaten, THUMBNAIL_PATH, RECORDINGS_PATH
from threading import Thread
import os
from MailClient import MailClient
import platform
from collections import deque
from DataPersistence import DataPersistence

MOTION_SEC = 5
CODECS = {"Linux": "avc1", "Darwin": "avc1", "Windows": "AVC1"}
THUMBNAIL_TYPE = ".jpg"
RECORDING_TYPE = ".mp4"
MEDIAN_RANGE = 15
FPS_CALCULATION_FRAMES = 100


class Timer:

    def __init__(self, seconds):
        self.__m_seconds = seconds
        self.__m_time_stamp = None

    def time_has_elpsed(self):
        if not self.__m_time_stamp:
            return True
        return (time.time() - self.__m_time_stamp) >= self.__m_seconds

    def reset(self):
        self.__m_time_stamp = time.time()

class ImageProcessing(Thread):

    m_fps = 30
    m_is_fps_set = False
    m_time_list = []
    m_dataBase = PipcoDaten.get_instance()
    m_images = deque(maxlen=MEDIAN_RANGE)
    m_last_motion_timer = Timer(MOTION_SEC)
    m_log_disabled_timer = Timer(30)
    m_frame_list = []
    m_out = None

    def __init__(self, normal = True):
        self.__m_run = True
        self.settings = None
        if normal:
            self.__m_mailclient = MailClient(ImageProcessing.m_dataBase)
        self.settings = self.m_dataBase.get_settings()
        self.m_stream = self.settings.streamaddress
        self.__m_storage_full = False
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
        update_timer = Timer(1)
        print("Enter Loop")
        while self.__m_run:
            time_start = time.time()
            ret, frame = cap.read()
        #   (read) If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file),
        #   the methods return false and the functions return NULL pointer.
            if ret:
                # Schritt 1: Farbbild zu Graubild
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Schritte 2-8 in check image
                motions = self.get_contours_of_moved_objects(gray_image)

                if len(motions):
                    if self.m_last_motion_timer.time_has_elpsed() and (self.settings.log_enabled or self.m_log_disabled_timer.time_has_elpsed()):
                        self.notify()
                        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        heigth = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        if not self.__m_storage_full and self.settings.log_enabled:
                            self.m_frame_list = []
                            idx = self.m_dataBase.get_free_index()
                            ouput_str = RECORDINGS_PATH + str(idx) + RECORDING_TYPE
                            self.m_out = cv2.VideoWriter(ouput_str, cv2.VideoWriter_fourcc(*CODECS[platform.system()]), self.m_fps, (int(width), int(heigth)))
                            print("Videocapture start")
                        elif not self.settings.log_enabled:
                            self.m_log_disabled_timer.reset()

                    #Schritt 9: Zeichne die Kanten in das neuste Frame
                    cv2.drawContours(frame, motions, -1, (0, 255, 0), 3)
                    if self.m_out:
                        self.m_last_motion_timer.reset()

                # end capture if writer is still set but no motion for n seconds
                # or clip gets too long
                if self.m_out and (self.m_last_motion_timer.time_has_elpsed()
                                     or len(self.m_frame_list) >= self.m_fps * self.settings.cliplength):
                    self.storage_manager()
                    self.reset_videocapture()
                    print("Videocapture end")

                # calculate fps if not already done
                if not self.m_is_fps_set:
                    self.m_time_list.append(time.time() - time_start)
                    if len(self.m_time_list) == FPS_CALCULATION_FRAMES:
                        sum = 0
                        for _time in self.m_time_list:
                            sum = sum+_time
                        self.m_fps = int(1/(sum/FPS_CALCULATION_FRAMES))
                        self.m_dataBase.m_stream_fps = self.m_fps
                        print("calculated FPS: " + str(self.m_fps))
                        self.m_is_fps_set = True

                # if videocapture still set write current frame to it
                if self.m_out:
                    self.m_out.write(frame)
                    self.m_frame_list.append(frame)

                frame = self.apply_brightness_contrast(frame, self.settings.brightness, self.settings.contrast)

                ret2, jpg = cv2.imencode('.jpg', frame)
                self.m_dataBase.set_image(jpg)

            elif self.m_stream.__contains__(".mkv"):
                # if video ist playing, reset video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # update settings every second
            if update_timer.time_has_elpsed():
                self.update_settings()
                update_timer.reset()

        #   verlaesst Funktion um run mit den neuen Parametern aufzurufen
            if self.m_stream_changed:
                return

    def get_contours_of_moved_objects(self, image):
        #old_image = ImageProcessing.m_images.get_last_image()
        image = self.apply_brightness_contrast(image, self.settings.brightness, self.settings.contrast)
        # Schritt 2: Entfernen von Rauschen und vereinheitlichen der Zahlen (Zeitstempel Kamera)
        new_image = cv2.GaussianBlur(image, (21, 21), 0)
        self.m_images.appendleft(new_image)
        # Schritt 3: Berechnen des Medians der alten Bilder
        old_image = self.get_median()

        if old_image is None:
            return []

        # Schritt 4: Subtraktion von Neues Image und Median image
        delta_frame = cv2.absdiff(new_image,old_image)
        # Schritt 5: Gross genuger Bereiche in neuem SW image uebernehmen
        thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
        # Schritt 6: Reduzieren der Flaechen
        thresh_frame = cv2.erode(thresh_frame, None, iterations=int(10*(1-self.settings.sensitivity)))
        # Schritt 7: vergroesern der uebrigen Flaechen
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        # Schritt 8: Extrahieren der Kanten in eine Liste
        (_, cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts):
            return cnts

        return []

    def get_median(self):
        if ImageProcessing.m_images:
            try:
                image_stack = np.concatenate([im[..., None] for im in ImageProcessing.m_images], axis=2)
                median_array = np.median(image_stack, axis=2)
                return np.asarray(median_array, np.uint8)
            except ValueError:
                return ImageProcessing.m_images[0]

    def notify(self):
        print("Motion detected")
        if self.settings.global_notify:
            self.__m_mailclient.notify_motion_detected()

    def update_settings(self):
        self.settings = self.m_dataBase.get_settings()
        if self.m_stream != self.settings.streamaddress:
            self.m_stream = self.settings.streamaddress
            self.m_stream_changed = True
            self.m_images.clear()
            self.m_time_list = []
            self.m_is_fps_set = False


    def save_thumbnail(self, image, id):
        small = cv2.resize(image, (0, 0), fx=0.2, fy=0.2)
        cv2.imwrite(THUMBNAIL_PATH + str(id) + THUMBNAIL_TYPE, small)


    #https://stackoverflow.com/questions/39308030/how-do-i-increase-the-contrast-of-an-image-in-python-opencv/41075028
    def apply_brightness_contrast(self, input_img, brightness=0, contrast=0):
        brightness = int(127*brightness)
        contrast = int(127*contrast)
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
        else:
            buf = input_img.copy()
        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
        return buf

    def storage_manager(self):
        self.__m_storage_full = int(DataPersistence.get_size_of_folder("data/") / 2 ** 20) >= self.settings.max_storage
        if self.__m_storage_full:
            self.__m_mailclient.notify_storage_full()
        else:
            idx = self.m_dataBase.add_log()
            self.save_thumbnail(self.m_frame_list[int(len(self.m_frame_list)/3)], idx)

    def reset_videocapture(self):
        self.m_out.release()
        self.m_out = None
        self.m_frame_list = []
        self.m_last_motion_timer.reset()
