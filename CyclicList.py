class cyclicList:
    __m_list = []
    __m_listSize = 0

    def __init__(self, size):
        self.m_listSize = size

    def push_front(self,Mat):
        self.__m_list.insert(0,Mat)
        while len(self.__m_list) > self.__m_listSize:
            self.__m_list.pop(self.__m_listSize)

    def getList(self):
        return self.__m_list

    def setListSize(self, int):
        self.__m_listSize(int)

    def flushList(self):
        self.__list.m_clear()
