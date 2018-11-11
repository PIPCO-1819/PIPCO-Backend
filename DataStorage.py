import CyclicList

class PipcoDaten:
    __m_instance = None
    __m_image = None
    __m_images = CyclicList.cyclicList(25)
    __m_log = []
    __m_emails = []
    m_lock = None

    def __init__(self):
        if self.__m_instance is not None:
            raise Exception("Something fucked up - Trying to init second instance")
        else:
            self.__m_instance = self

    @staticmethod
    def getInstance(self):
        if self.__m_instance is None:
            self.__m_instance = PipcoDaten()
        return self.__m_instance

#   addImage greift auf die Funktion push_front aus CyclicList zu.
    # Die ältesten Bilder automatisch gelöscht
    def addImage(self, image):
        self.__m_images.push_front(image)

#   getImages greift auf die Funktion getList aus CyclicList zu.
    # Gibt die direkte Liste zurück. Sollte als const List betrachtet werden
    def getImages(self):
        return self.__m_images.getList()

    def addMail(self, mail):
        self.__m_emails.append(mail)

    def removeMail(self, mail):
        self.__m_emails.remove(mail)

    def getMails(self):
        return self.__m_emails

    def addLog(self, log):
        self.m_log.insert(0, log)

    def removeLog(self, log):
        PipcoDaten.m_log.remove(log)

