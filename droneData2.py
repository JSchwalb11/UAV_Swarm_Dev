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
from dronekit import LocationGlobalRelative


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
        self.ip = config.ip
        self.webport = config.webport

    # =============================MEMBER FUNCTIONS==========================================================
    # =======================================================================================================

    def add_drone(self, drone):
        # This function is used to add a drone to the swarm.
        self.swarm.append(drone)
        print("Drone: {0}".format(drone.get_drone_data()))

    def remove_drone(self, droneID):
        found = False
        for idx, drone in enumerate(self.swarm):
            if drone["id"] == droneID:
                del self.swarm[idx]
                found = True

        print("Swarm: {0}".format(json.dumps(self.swarm)))
        return found

    def find_drone_by_id(self, droneID):
        if self.drone_index(droneID) >= 0:
            return self.swarm[self.drone_index(droneID)]
        return "No Drone exists with ID of " + str(droneID)

    def drone_index(self, droneID):
        for idx, drone in enumerate(self.swarm):
            if drone["id"] == droneID:
                return idx
        return -1

    def swarm_size(self):
        return self.swarm.__len__()

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
            print(drone.get_drone_data())

    def get_swarm_data(self, route):
        url = "http://" + self.ip + ":" + str(self.webport) + route
        try:
            r = requests.get(url)
            json_data = json.loads(r.text)
            parsed_data = Config(json_data)
            print("\nServer Responded With: " + str(r.status_code) + " " + str(r.text) + "\n")
            return parsed_data
        except requests.HTTPError:
            print("HTTP " + str(requests.HTTPError))
            return "NO_DATA"

    def wait_for_swarm_ready(self):
        # drone_data.Drones[drone_id][1 (indexing bug)].get("ip")
        swarm_ready_status = []

        while not assert_true(swarm_ready_status):
            swarm_params = self.get_swarm_data("/Swarm")
            swarm_size = swarm_params.Drones.__len__()
            print("Found " + str(swarm_size) + "Drones in the Swarm.")

            for idx, drone in enumerate(swarm_params.Drones):
                if not swarm_params:
                    print("No Drones Found in the Swarm.")
                else:
                    if not swarm_params.Drones[idx][1]:
                        print("No Drones Found in the Swarm.")
                    else:
                        print("Drone: " + str(swarm_params.Drones[idx][1].get("id") + " found in swarm"))
                        swarm_ready_status.append(1)
                        time.sleep(1)
            assert_true(swarm_ready_status)
        #if swarm_is_not_ready and all drones have been checked, do loop again
        print("Swarm is ready!")

    def goto_formation(self, formation, formationAltitude, bool):
        # Formation on X,Y axes

        swarm_data = self.get_swarm_data("/Swarm")
        #Form up on first drone in swarm for now
        head_drone_data = swarm_data.Drones[0][1]
        head_drone_loc = LocationGlobalRelative(head_drone_data.get("latitude"),head_drone_data.get("longitude"),head_drone_data.get("altitude"))

        """
        Transition into formation so they don't crash
        Safe altitude is different for some drones so they don't maneuver into position at the same altitude

        3 Steps:
            1. Move to a safe altitude to manuver in
            2. Move to the position inside the formation it should be in
            3. Move to the correct altitude inside the formation

        Formation occurs on drone object (ID:1).
        ID:1 should only change its altitude.
        
        """

        if formation == "triangle":
            for idx, drone in enumerate(swarm_data.Drones):
                if drone.id == 1:
                    self.swarm[drone.id-1].simple_goto(head_drone_loc.lat,head_drone_loc.lon,formationAltitude)

                elif drone.id == 2:

                    #Maneuver 5 metres below formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude - 5
                    self.swarm[drone.id-1].simple_goto(drone.location.global_frame.lat,drone.location.global_frame.lon,safeAltitude)
                    self.swarm[drone.id-1].simple_goto(head_drone_loc.lat - .0000027, head_drone_loc.lon - .0000027, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat - .0000027, head_drone_loc.lon - .0000027, formationAltitude)

                elif drone.id == 3:

                    #Maneuver 5 metres above formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude + 5
                    self.swarm[drone.id - 1].simple_goto(drone.location.global_frame.lat, drone.location.global_frame.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat + .0000027, head_drone_loc.lon - .0000027, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat + .0000027, head_drone_loc.lon - .0000027, formationAltitude)

        elif formation == "stacked":
            # Special formation altitude represents the separation on the Z axis between the drones
            special_formation_altitude = 3

            for idx, drone in enumerate(swarm_data.Drones):
                if drone.id == 1:

                    #Maneuver to formation altitude
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat,head_drone_loc.lon,formationAltitude)

                elif drone.id == 2:

                    #Maneuver 5 metres below formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude - 5
                    self.swarm[drone.id - 1].simple_goto(drone.location.global_frame.lat, drone.location.global_frame.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon, formationAltitude - special_formation_altitude)

                elif drone.id == 3:

                    # Maneuver 5 metres above formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude + 5
                    self.swarm[drone.id - 1].simple_goto(drone.location.global_frame.lat, drone.location.global_frame.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon, formationAltitude + special_formation_altitude)

        elif formation == "xaxis":
            for idx, drone in enumerate(swarm_data.Drones):
                if drone.id == 1:

                    # Maneuver to formation altitude
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon, formationAltitude)

                elif drone.id == 2:

                    # Maneuver 5 metres below formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude - 5
                    self.swarm[drone.id - 1].simple_goto(drone.location.global_frame.lat, drone.location.global_frame.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat - .0000027, head_drone_loc.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat - .0000027, head_drone_loc.lon, formationAltitude)

                elif drone.id == 3:

                    # Maneuver 5 metres above formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude + 5
                    self.swarm[drone.id - 1].simple_goto(drone.location.global_frame.lat, drone.location.global_frame.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat + .0000027, head_drone_loc.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat + .0000027, head_drone_loc.lon, formationAltitude)

        elif formation == "yaxis":
            for idx, drone in enumerate(swarm_data.Drones):
                if drone.id == 1:

                    # Maneuver to formation altitude
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon, formationAltitude)

                elif drone.id == 2:

                    # Maneuver 5 metres below formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude - 5
                    self.swarm[drone.id - 1].simple_goto(drone.location.global_frame.lat, drone.location.global_frame.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon - .0000027, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon - .0000027, formationAltitude)

                elif drone.id == 3:

                    # Maneuver 5 metres above formation altitude
                    if bool:
                        safeAltitude = formationAltitude
                    elif not bool:
                        safeAltitude = formationAltitude + 5
                    self.swarm[drone.id - 1].simple_goto(drone.location.global_frame.lat, drone.location.global_frame.lon, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon + .0000027, safeAltitude)
                    self.swarm[drone.id - 1].simple_goto(head_drone_loc.lat, head_drone_loc.lon + .0000027, formationAltitude)

    def launch_swarm(self, aTargetAltitude):
        for idx, drone in enumerate(self.swarm):
            drone.arm_and_takeoff(aTargetAltitude)

def assert_true(obj):
    if obj.__class__ is list:
        if obj:
            for idx in range(0,obj.__len__()):
                if obj[idx] == 1:
                    continue
                else:
                    return False
            return True
        else:
            print("Empty List")
            return False
    else:
        print("Object is not a list.")