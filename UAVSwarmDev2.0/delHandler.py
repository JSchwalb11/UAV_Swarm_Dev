import tornado
from tornado import web
from flask import json


class delHandler(tornado.web.RequestHandler):
    def __init__(self, swarm):
        self.swarm = swarm

    def get(self, droneID):
        drone = self.swarm.getDrone(self.swarm, droneID)
        result = self.swarm.removeDrone(drone['id]'])
        if result:
            self.write("Deleted Drone: {0} successfully".format(id))
            self.set_status(200)
        else:
            self.write("Drone '{0}' not found".format(id))
            self.set_status(404)

    def post(self):
        data = json.loads(self.request.body)
        id = data["id"]
        result = self.swarm.removeDrone(id)
        if result:
            self.write("Deleted Drone: {0} successfully".format(id))
            self.set_status(200)
        else:
            self.write("Drone '{0}' not found".format(id))
            self.set_status(404)