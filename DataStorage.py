import datetime
import CyclicList
from collections import OrderedDict

USER = "user"
PASSWORD = "geheim"


class PipcoDaten:
    __m_instance = None
    m_lock = None

    def __init__(self):
        if self.__m_instance is not None:
            raise Exception("Something fucked up - Trying to init second instance")
        else:
            print("New PipcoData")
            self.__m_log = AutoIdDict()
            self.__m_emails = AutoIdDict()
            self.__m_instance = self
            self.__m_image = None
            self.__m_images = CyclicList.cyclicList(25)
            self.__m_user = USER
            self.__m_password = PASSWORD


    @staticmethod
    def getInstance():
        if PipcoDaten.__m_instance is None:
            PipcoDaten.__m_instance = PipcoDaten()
        return PipcoDaten.__m_instance

#   addImage greift auf die Funktion push_front aus CyclicList zu.
    # Die ältesten Bilder automatisch gelöscht
    def addImage(self, image):
        self.__m_images.push_front(image)

#   getImages greift auf die Funktion getList aus CyclicList zu.
    # Gibt die direkte Liste zurück. Sollte als const List betrachtet werden
    def getImages(self):
        return self.__m_images.getList()

    def addMail(self, mail):
        return self.__m_emails.append(mail)

    def removeMail(self, id):
        self.__m_emails.__delitem__(id)

    def getMails(self):
        return self.__m_emails

    def set_image(self, image):
        self.__m_image = image

    def get_image(self):
        return self.__m_image

    def get_log(self):
        return self.__m_log

    def get_log_page(self, page, batchsize):
        selected = OrderedDict()
        for idx, key in enumerate(list(self.__m_log.keys())[int(page)*int(batchsize):]):
            selected[key] = self.__m_log[key]
            if int(batchsize)-1 == idx:
                return selected
        return selected

    def addLog(self):
        idx = self.__m_log.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return idx

    def check_login(self, user, password):
        return self.__m_user == user and self.__m_password == password

    def removeLog(self, id):
        self.__m_log.__delitem__(id)



class AutoIdDict(OrderedDict):

    def append(self, val):
        if val in self.values():
            return False
        for idx, elem in enumerate(sorted(self.keys())):
            if idx < elem:
                self[idx] = val
                return idx
        self[len(self)] = val
        return len(self)
