import os
import time

class getLocalTime():

    def __init__(self,id):
        self.id = id
        self.folder = "logs/id:" + self.id
        self.localtime = time.strftime("%b %d %I:%M:%S", time.localtime(time.time()))

    def getFile(self):
        print(self.localtime)
        return self.localtime