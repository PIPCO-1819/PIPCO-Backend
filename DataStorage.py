import datetime
import DataPersistence
from threading import Lock
import copy

USER = "user"
PASSWORD = "geheim"
THUMBNAIL_PATH = "data/recordings/thumbnails/"
RECORDINGS_PATH = "data/recordings/"


class PipcoDaten:
    __m_instance = None
    m_lock = None

    def __init__(self):
        if self.__m_instance is not None:
            raise Exception("Something fucked up - Trying to init second instance")
        else:
            self.m_data_persistence = DataPersistence.DataPersistence(self)
            self.__m_emails_lock = Lock()
            self.__m_log_lock = Lock()
            self.__m_setting_lock = Lock()
            self.__m_settings = self.m_data_persistence.load_settings()
            self.__m_emails = self.m_data_persistence.load_emails()
            self.__m_log = self.m_data_persistence.load_logs()
            if not self.__m_log:
                self.__m_log = AutoIdDict()
            if not self.__m_emails:
                self.__m_emails = AutoIdDict()
            if not self.__m_settings:
                self.__m_settings = Settings()
            self.__m_instance = self
            self.__m_image = None
            self.__m_user = USER
            self.__m_password = PASSWORD

    @staticmethod
    def get_instance():
        if PipcoDaten.__m_instance is None:
            PipcoDaten.__m_instance = PipcoDaten()
        return PipcoDaten.__m_instance

    def toggle_mail_notify(self, id):
        with self.__m_emails_lock:
            state = not self.__m_emails[int(id)].notify
            self.__m_emails[int(id)].notify = state
            self.m_data_persistence.save_emails(self.__m_emails)
            return state

    def add_mail(self, address):
        with self.__m_emails_lock:
            ret = self.__m_emails.append(Mail(address))
            self.m_data_persistence.save_emails(self.__m_emails)
            return ret

    def remove_mail(self, id):
        with self.__m_emails_lock:
            self.__m_emails.__delitem__(id)
            self.m_data_persistence.save_emails(self.__m_emails)
            return id

    def get_mails(self):
        with self.__m_emails_lock:
            ret = copy.deepcopy(self.__m_emails)
            return ret

    def get_settings(self):
        with self.__m_setting_lock:
            ret = copy.copy(self.__m_settings)
            return ret

    def change_settings(self, sensitivity=None, brightness=None, contrast=None, streamaddress=None, global_notify=None):
        with self.__m_setting_lock:
            ret = {}
            if sensitivity is not None:
                ret["sensitivity"] = sensitivity
                self.__m_settings.sensitivity = float(sensitivity)
            if brightness is not None:
                ret["brightness"] = brightness
                self.__m_settings.brightness = float(brightness)
            if contrast is not None:
                ret["contrast"] = contrast
                self.__m_settings.contrast = float(contrast)
            if streamaddress is not None:
                ret["streamaddress"] = streamaddress
                self.__m_settings.streamaddress = streamaddress
            if global_notify is not None:
                ret["global_notify"] = global_notify
                self.__m_settings.global_notify = bool(global_notify)
            self.m_data_persistence.save_settings(self.__m_settings)
            return ret

    def set_image(self, image):
        self.__m_image = image

    def get_image(self):
        return self.__m_image

    def get_log_page(self, page, batchsize):
        with self.__m_log_lock:
            selected = {}
            for idx, key in enumerate(sorted(self.__m_log.keys(), reverse=True)[int(page)*int(batchsize):]):
                selected[key] = copy.copy(self.__m_log[key])
                if int(batchsize)-1 == idx:
                    return selected
            return selected

    def get_free_index(self):
        with self.__m_log_lock:
            return self.__m_log.get_free_index()

    def add_log(self):
        with self.__m_log_lock:
            idx = self.__m_log.get_free_index()
            idx = self.__m_log.append(Log(idx))
            self.m_data_persistence.save_logs(self.__m_log)
            return idx

    def check_login(self, user, password):
        return self.__m_user == user and self.__m_password == password

    def remove_log(self, id):
        with self.__m_log_lock:
            self.__m_log.__delitem__(id)
        return id

class AutoIdDict(dict):

    def __init__(self, list=None):
        if list:
            for val in list:
                self[val.id] = val
        super(dict, self).__init__()

    def append(self, val):
        if val in self.values():
            return -1
        index = self.get_free_index()
        val.id = index
        self[index] = val
        return index

    def get_free_index(self):
        if self:
            ret = sorted(self.keys())[-1]+1
            return ret
        else:
            return 0


class Mail:
    def __init__(self, address, id=0, notify=True):
        self.address = address
        self.notify = notify
        self.id = id

    def __eq__(self, other):
        return self.address == other.address and \
               self.notify == other.notify


class Log:
    def __init__(self, id=0, timestamp=None, message=""):
        if not timestamp:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.message = message
        self.timestamp = timestamp
        self.id = id


class Settings:

    def __init__(self, sensitivity=0.5, brightness=0.5, contrast=0.5, streamaddress="", global_notify=True):
        self.sensitivity = sensitivity
        self.streamaddress = streamaddress
        self.brightness = brightness
        self.contrast = contrast
        self.global_notify = global_notify
