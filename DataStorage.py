import datetime
import cv2
import CyclicList

class PipcoDaten:
    m_instance = None
    m_image = CyclicList.cyclicList(25)
    m_log = []
    m_emails = []
    m_lock = None

    @staticmethod
    def getInstance(self):
        if PipcoDaten.m_instance is None:
            PipcoDaten.m_instance = PipcoDaten.__init__(self)
        return PipcoDaten.m_instance

#   addImage greift auf die Funktion push_front aus CyclicList zu.
    # Die ältesten Bilder automatisch gelöscht
    def addImage(self, image):
        PipcoDaten.m_image.push_front(image)

#   getImages greift auf die Funktion getList aus CyclicList zu.
    # Gibt die direkte Liste zurück. Sollte als const List betrachtet werden
    def getImages(self):
        return PipcoDaten.m_image.getList()

    def addMail(self, mail):
        PipcoDaten.m_emails.append(mail)

    def removeMail(self, mail):
        PipcoDaten.m_emails.remove(mail)

    def addLog(self, log):
        PipcoDaten.m_log.insert(0, log)

    def removeLog(self, log):
        PipcoDaten.m_log.remove(log)

