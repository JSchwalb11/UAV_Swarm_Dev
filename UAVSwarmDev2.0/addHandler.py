import tornado
from flask import json
from droneData2 import Swarm


class addHandler(tornado.web.RequestHandler):

    def __init__(self, swarm):
        self.swarm = swarm

    def get(self, droneID):
        self.write(Swarm.get_drone(self.swarm, droneID))

    def post(self):
        data = json.loads(self.request.body)
        if Swarm.drone_index(self.swarm, data['id']):
            self.write(Swarm.update_drone_Info(self.swarm, data))
        else:
            self.write(Swarm.add_drone(self.swarm, data))
