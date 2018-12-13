import cv2
import time
import numpy as np
import CyclicList
from DataStorage import PipcoDaten, THUMBNAIL_PATH, RECORDINGS_PATH
from threading import Thread
import os
from MailClient import MailClient
import platform

MOTION_SEC = 5
CODECS = {"Linux": "x264", "Darwin": "avc1", "Windows": "AVC1"}
THUMBNAIL_TYPE = ".jpg"
RECORDING_TYPE = ".mp4"
MEDIAN_RANGE = 15

class ImageProcessing(Thread):

    m_fps = 15
    m_is_fps_set = False
    m_time_list = []
    m_dataBase = PipcoDaten.get_instance()
    m_images = CyclicList.cyclicList(MEDIAN_RANGE)
    m_lastMotionTime = 0
    m_idx = 0
    m_thumbnail = None

    def __init__(self, debug):
        self.__m_run = True
        self.__m_debug = debug
        self.__m_mailclient = MailClient(ImageProcessing.m_dataBase)
        self.settings = self.m_dataBase.get_settings()

        if debug:
            self.m_stream = "videosamples/sample2.mkv"
            self.m_dataBase.change_settings(streamaddress=self.m_stream)
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
        out = None
        frame_list = []
        storage_full = False
        while self.__m_run:
            time_start = time.time()
            ret, frame = cap.read()
        #   (read) If no frames has been grabbed (camera has been disconnected, or there are no more frames in video file),
        #   the methods return false and the functions return NULL pointer.
            if ret:
                # Schritt 1: Farbbild zu Graubild
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Schritte 2-8 in check image
                motion = self.check_image(gray_image)
                if self.compare_time(MOTION_SEC):
                    if len(motion):
                        self.notify()
                        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        heigth = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        if not storage_full and self.settings.log_enabled:
                            frame_list = []
                            idx = self.m_dataBase.get_free_index()
                            ouput_str = RECORDINGS_PATH + str(idx) + RECORDING_TYPE

                            out = cv2.VideoWriter(ouput_str, cv2.VideoWriter_fourcc(*CODECS[platform.system()]), self.m_fps, (int(width), int(heigth)))

                            print("Videocapture start")

                    else:
                        if out is not None:
                            storage_full = int(self.get_size_of_folder("data/") / 2 ** 20) >= self.settings.max_storage
                            if storage_full:
                                self.__m_mailclient.storage_full()
                            else:
                                idx = self.m_dataBase.add_log()
                                self.save_thumbnail(frame_list[int(len(frame_list)/3)], idx)
                            print("Videocapture end")
                            out.release()
                            out = None
                            frame_list = []

                if len(motion):
                    #Schritt 9: Zeichne die Kanten in das neuste Frame
                    cv2.drawContours(frame, motion, -1, (0, 255, 0), 3)
                    self.m_lastMotionTime = int(round(time.time() * 1000))

                if self.m_is_fps_set is False:
                    self.m_time_list.append(time.time() - time_start)

                    if len(self.m_time_list) == 100:
                        sum = 0
                        for _time in self.m_time_list:
                            sum = sum+_time
                        self.m_fps = int(1/(sum/100))
                        print(self.m_fps)
                        self.m_is_fps_set = True

                if out is not None:
                    out.write(frame)
                    frame_list.append(frame)

                    if len(frame_list) == self.m_fps * self.m_dataBase.get_settings().cliplength:
                        storage_full = int(self.get_size_of_folder("data/") / 2 ** 20) >= self.settings.max_storage
                        if storage_full:
                            self.__m_mailclient.storage_full()
                        else:
                            idx = self.m_dataBase.add_log()
                            self.save_thumbnail(frame_list[int(len(frame_list)/3)], idx)
                        print("Videocapture end")
                        out.release()
                        out = None
                        frame_list = []

                frame = self.apply_brightness_contrast(frame, self.settings.brightness, self.settings.contrast)
                ret2, jpg = cv2.imencode('.jpg', frame)
                self.m_dataBase.set_image(jpg)

            elif self.__m_debug:
                # if video ist playing, reset video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # update settings every second
            update_counter += 1
            if update_counter >= self.m_fps:
                update_counter = 0
                self.update_settings()

        #   verlaesst Funktion um run mit den neuen Parametern aufzurufen
            if self.m_stream_changed:
                return

    def check_image(self,image):
        #old_image = ImageProcessing.m_images.get_last_image()
        image = self.apply_brightness_contrast(image, self.settings.brightness, self.settings.contrast)
        # Schritt 2: Entfernen von Rauschen und vereinheitlichen der Zahlen (Zeitstempel Kamera)
        new_image = cv2.GaussianBlur(image,(21,21),0)
        self.push_front(new_image)
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
        if ImageProcessing.m_images.get_list():
            image_stack = np.concatenate([im[..., None] for im in ImageProcessing.m_images.get_list()], axis=2)
            median_array = np.median(image_stack, axis=2)
            return np.asarray(median_array, np.uint8)

    def notify(self):
        print("Motion detected")
        if not self.__m_debug and self.settings.global_notify:
            self.__m_mailclient.notify_users()

    def update_settings(self):
        self.settings = self.m_dataBase.get_settings()
        if self.m_stream != self.settings.streamaddress:
            self.m_stream = self.settings.streamaddress
            self.m_stream_changed = True

    def push_front(self, image):
        self.m_images.push_front(image)

#   dauer von x Sekunden abgelaufen
    def compare_time(self, val):
        now = int(round(time.time()*1000))

        if self.m_lastMotionTime is not None:
            # vergleich ob x Sekunden abgelaufen sind
            return (now-self.m_lastMotionTime) >= 1000*val

        return True

    def save_thumbnail(self, image, id):
        small = cv2.resize(image, (0, 0), fx=0.2, fy=0.2)
        cv2.imwrite(THUMBNAIL_PATH + str(id) + THUMBNAIL_TYPE, small)

    def get_size_of_folder(self, start_path):
        total_size = 0
        for path, dirs, files in os.walk(start_path):
            for f in files:
                fp = os.path.join(path, f)
                total_size += os.path.getsize(fp)
        return total_size

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
