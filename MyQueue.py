
import heapq
class PriorityQ:
    def __init__(self):
        self.data = []

    def push(self, uID ,curNode, dis, p):
        heapq.heappush(self.data, (uID, curNode, dis, p))

    def pop(self):
        return heapq.heappop(self.data)

    def getSize(self):
        return len(self.data)

    def peek(self):
        return self.data[0]
