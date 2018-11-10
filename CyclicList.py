class cyclicList:
    m_list = []
    m_listSize = 0

    def __init__(self, size):
        cyclicList.m_listSize = size

    def push_front(self,Mat):
        cyclicList.m_list.insert(0,Mat)
        while len(cyclicList.m_list) > cyclicList.m_listSize:
            list.pop(cyclicList.m_listSize)

    def getList(self):
        return cyclicList.m_list

    def flushList(self):
        cyclicList.list.m_clear()
