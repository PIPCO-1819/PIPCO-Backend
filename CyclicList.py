class cyclicList:

    def __init__(self, size):
        self.__m_list = []
        self.__m_listSize = size

    def push_front(self,Mat):
        self.__m_list.insert(0,Mat)
        while len(self.__m_list) > self.__m_listSize:
            self.__m_list.pop(self.__m_listSize)

    def get_list(self):
        return self.__m_list

    def set_list_size(self, int):
        self.__m_listSize(int)

    def flush_list(self):
        self.__list.m_clear()

    def get_size(self):
        return len(self.__m_list)

#   returns the newest image
    def get_last_image(self):
        if len(self.__m_list) != 0:
            return self.__m_list[0]
        else:
            return None
