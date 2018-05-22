# =============================droneData.py===================================================================
# Author: Martin Pozniak, Joey Schwalb
# Desc: This class is used by server.py to control and keep track of the swarm data.
# Creation Date: 12/~/2017
# =============================================================================================================

# --------------What the Drone data structure will look like--------------
# -------This is not the actual object used to store active drones--------
# ----a one element list, which contains a dictionary--------------------
# -----whose keys are the Drone ID, and whose value is another dict containing the params------
from flask import json
#from addHandler import addHandler
#from delHandler import delHandler

Drones = [
    {
        "id": '1',
        "ip": "192.168.x.x",
        "latitude": "~",
        "longitude": "~",
        "altitude": "~",
        "armed": "False",
        "mode": "vehicle.mode"
    },
    {
        "id": '2',
        "ip": "192.168.x.x",
        "latitude": '~',
        "longitude": '~',
        "altitude": '~',
        "armed": "False",
        "mode": "vehicle.mode"
    }
]


# --------------------^^For Visual Aid Only^^----------------------------

# =============================SWARM CLASS | CONTAINS SWARM OPERATIONS===================================
# =======================================================================================================
class Swarm:

    # =============================SWARM CONSTRUCTOR=========================================================
    # =======================================================================================================
    def __init__(self):
        self.swarm = []

    # =============================MEMBER FUNCTIONS==========================================================
    # =======================================================================================================

    def addDrone(self, drone):
        # This function is used to add a drone to the swarm.
        self.swarm.append(drone.get_drone_data())
        print("Drone: {0}".format(drone.get_drone_data()))

    def removeDrone(self, droneID):
        found = False
        for idx, drone in enumerate(self.swarm):
            if drone["id"] == droneID:
                found = True
                del self.swarm[idx]

        print("Swarm: {0}".format(json.dumps(self.swarm)))
        return found

    def findDroneByID(self, droneID):
        if self.droneIndex(droneID) >= 0:
            return self.swarm[self.droneIndex(droneID)]
        return "No Drone exists with ID of " + (str)(droneID)

    def droneIndex(self, droneID):
        for idx, drone in enumerate(self.swarm):
            if drone["id"] == droneID:
                return idx
        return -1

    def swarmSize(self):
        for idx in enumerate(self.swarm):
            pass
        return idx

    def updateDroneInfo(self, newData):
        indxDroneToUpdate = self.droneIndex(newData["id"])
        drone_info = {
            'id': newData.id,
            'ip': newData.ip,
            'latitude': newData.location.global_frame.lat,
            'longitude': newData.location.global_frame.lon,
            'altitude': newData.location.global_relative_frame.alt,
            'airspeed': newData.vehicle.airspeed,
            'armed': newData.armed,
            'mode': newData.mode.name
        }

        self.swarm[indxDroneToUpdate] = json.loads(drone_info)
        print("Updated Drone: " + str(drone_info["id"]) + " with new data!")

    def getSwarm(self):
        return self.swarm

    def getDrone(self, droneID):
        return json.loads(self.swarm[self.droneIndex(droneID)])

    def listSwarm(self):
        for idx, drone in enumerate(self.swarm):
            print(drone.toString())
