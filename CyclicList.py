class cyclicList:
    list = []
    listSize = 0

    def __init__(self, size):
        cyclicList.listSize = size

    def push_front(self,Mat):
        cyclicList.list.insert(0,Mat)
        while len(cyclicList.list) > cyclicList.listSize:
            list.pop(cyclicList.listSize)

    def getList(self):
        return cyclicList.list
