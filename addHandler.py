import tornado
from flask import json
from droneData2 import Swarm


class addHandler(tornado.web.RequestHandler):

    def __init__(self, swarm):
        self.swarm = swarm

    def get(self, droneID):
        self.write(Swarm.getDrone(self.swarm, droneID))

    def post(self):
        data = json.loads(self.request.body)
        if Swarm.droneIndex(self.swarm, data['id']):
            self.write(Swarm.updateDroneInfo(self.swarm, data))
        else:
            self.write(Swarm.addDrone(self.swarm, data))
