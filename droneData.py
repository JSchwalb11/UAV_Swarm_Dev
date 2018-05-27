# =============================droneData.py===================================================================
# Author: Martin Pozniak, Joey Schwalb
# Desc: This class is used by server.py to control and keep track of the swarm data.
# Creation Date: 12/~/2017
# =============================================================================================================

# --------------What the Drone data structure will look like--------------
# -------This is not the actual object used to store active drones--------
# ----a one element list, which contains a dictionary--------------------
# -----whose keys are the Drone ID, and whose value is another dict containing the params------
#from flask import json
import json
import time
import requests
from config import Config
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
    def __init__(self, config):
        self.swarm = []
        self.webserver = config.Swarm.ip
        self.webport = config.Swarm.webport

    # =============================MEMBER FUNCTIONS==========================================================
    # =======================================================================================================

    def add_drone(self, drone):
        # This function is used to add a drone to the swarm.
        self.swarm.append(drone.get_drone_data())
        print("Drone: {0}".format(drone.get_drone_data()))

    def remove_drone(self, droneID):
        found = False
        for idx, drone in enumerate(self.swarm):
            if drone["id"] == droneID:
                found = True
                del self.swarm[idx]

        print("Swarm: {0}".format(json.dumps(self.swarm)))
        return found

    def find_drone_by_id(self, droneID):
        if self.drone_index(droneID) >= 0:
            return self.swarm[self.drone_index(droneID)]
        return "No Drone exists with ID of " + (str)(droneID)

    def drone_index(self, droneID):
        for idx, drone in enumerate(self.swarm):
            if drone["id"] == droneID:
                return idx
        return -1

    def swarm_size(self):
        for idx in enumerate(self.swarm):
            pass
        return idx

    def update_drone_Info(self, newData):
        indxDroneToUpdate = self.drone_index(newData["id"])
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

    def get_swarm(self):
        return self.swarm

    def get_drone(self, droneID):
        return json.loads(self.swarm[self.drone_index(droneID)])

    def list_swarm(self):
        for idx, drone in enumerate(self.swarm):
            print(drone.to_string())

    def get_swarm_data(self, route):
        url = self.webserver + route
        try:
            r = requests.get(url)
            print("\nServer Responded With: " + str(r.status_code) + " " + str(r.text) + "\n")
            return Config(json.loads(r.text))
        except requests.HTTPError:
            print("HTTP " + str(requests.HTTPError))
            return "NO_DATA"

    def wait_for_swarm_ready(self):
        swarm_ready_status = []

        while not assert_true(swarm_ready_status):
            swarm_params = self.get_swarm_data("/Swarm")
            swarm_size = swarm_params.__len__()
            print("Found " + (str)(swarm_size) + "Drones in the Swarm.")

            for idx, drone in enumerate(swarm_params):
                if swarm_params == "NO_DATA":
                    print("No Drones Found in the Swarm.")
                else:
                    if not swarm_params.Drones:
                        print("No Drones Found in the Swarm.")
                    else:
                        print("Drone: " + (str)(swarm_params.Drones[idx].id) + " found in swarm")
                        time.sleep(1)

            #if swarm_is_not_ready and all drones have been checked, do loop again
        print("Swarm is ready!")

def assert_true(obj):
    if obj.__class__ is list:
        if obj:
            for idx in enumerate(obj):
                if obj[idx] == True:
                    continue
                else:
                    return False
        else:
            print("Empty List")
            return False
    else:
        print("Object is not a list.")