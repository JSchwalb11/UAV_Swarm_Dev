import json

import logging

from mission import Mission
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import requests
import time
import dronekit_sitl
import argparse


class Drone:
    formation = "triangle"

    def __init__(self, config):
        self.default_webserver_ip = config.ip #'192.168.1.1'  # change depending on drone's role - 192.168.1.[1-10]
        self.default_port = config.port
        self.default_webserver_port = config.webport
        self.id = config.id
        self.ip = config.ip
        self.sitl = config.sitl
        #        self.port = port
        self.connection_string = dronekit_sitl.start_default().connection_string()#str(self.ip) + ":" + str(self.default_port)
        self.webserver = str(self.ip) + ":" + str(self.default_webserver_port)
        print('\nConnecting to vehicle on: %s\n' % self.connection_string)
        self.vehicle = connect(self.connection_string)
        self.drone_data = self.get_drone_data()
        self.mission = Mission(self.vehicle)
        # logger config
        self.logger = logging.getLogger("drone" + (str)(self.id) + "_log")
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("drone" + (str)(self.id) + "_log")
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        # Always add the drone to swarm last.
        #print(self.get_drone_data())

    # =============================ATTRIBUTE LISTENER CALLBACKS==============================================
    # =======================================================================================================
    def location_callback(self, self2, attr_name, value):  # value type is dronekit.LocationGlobalRelative
        if True:  # Replace tru with a way to check if any values in location object changed
            try:
                self.send_data_to_server("/dronedata", self.get_drone_data())
                alt = self.vehicle.location.global_relative_frame.alt
                # print("Alt:",alt)
                if (
                        alt < 2 and self.vehicle.mode.name == "GUIDED"):  # if the vehicle is in guided mode and alt is less than 2m slow it the f down
                    self.vehicle.airspeed = .2
            except:
                self.logger.info("Error communicating with server1")

        else:
            self.logger.info("Location Object Didn't Change")

    def armed_callback(self, self2, attr_name, value):
        self.logger.info("Armed Status Of Drone: " + value)
        try:
            self.send_data_to_server("/dronedata", self.get_drone_data())
        except:
            self.logger.info("Error communicating with server2")

    def mode_callback(self, self2, attr_name, value):
        self.logger.info("Mode Of Drone: " + str(value))
        try:
            self.send_data_to_server("/dronedata", self.get_drone_data())
        except:
            self.logger.info("Error communicating with server3")

    # =============================COMMUNICATION TO SERVER===================================================
    # =======================================================================================================
    def send_data_to_server(self, route, data):
        url = self.webserver + route + "/" + str(self.id)
        try:
            r = requests.post(url, json.dumps(data))
            self.logger.info("\nServer Responded With: " + str(r.status_code) + " " + str(r.text) + "\n")
        except requests.HTTPError:
            self.logger.info(str(requests.HTTPError))

    def get_data_from_server(self, route, id):
        url = self.webserver + route + "/" + str(id)
        try:

            r = requests.get(url)
            self.logger.info("\nServer Responded With: " + str(r.status_code) + " " + (str)(json.dumps(data)) + "\n")
            return json.loads(r.text)

        except requests.HTTPError:
            self.logger.info("Error Getting Data From The Server, Is It Running?")  # printed not loggered?
            return "NO_DATA"

        # used to see how the server is responding. Maybe just print to log and not console

        # self.logger.info("\n\nRETURNING: " + json.dumps(data) + "\n\n")

    def add_to_swarm(self):
        self.send_data_to_server("/adddrone", self.get_drone_data())

    def remove_from_swarm(self):
        return self.send_data_to_server("/removedrone", self.get_drone_data())

    def get_swarm_data(self):
        return self.get_data_from_server("/swarmdata", None)

    def abort_if_drone_doesnt_exist(self):
        if Swarm.droneExists(Drone.id):
            abort(404, message="Drone {} doesn't exist".format(Drone.id))

    # =============================VEHICLE INFORMATION FUNCTIONS=================================================
    # =======================================================================================================
    def get_drone_data(self):
        # creates a dictionary object out of the drone data
        return type('obj', (object,), {
                                        "id": self.id,
                                        "ip": self.ip,
                                        "airspeed": self.vehicle.airspeed,
                                        "latitude": self.vehicle.location.global_frame.lat,
                                        "longitude": self.vehicle.location.global_frame.lon,
                                        "altitude": self.vehicle.location.global_relative_frame.alt,
                                        "armed": self.vehicle.armed,
                                        "mode": self.vehicle.mode.name
                                      }
                    )

    # =============================VEHICLE CONTROL FUNCTIONS=================================================
    # =======================================================================================================
    def set_parameter(self, paramName, value):  # Sets a specified param to specified value
        self.vehicle.parameters[paramName] = value

    def set_airspeed(self, value):
        self.vehicle.airspeed = value

    def set_mode(self, mode):
        self.vehicle.mode = VehicleMode(mode)

    def set_formation(self, formationName):
        self.formation = formationName

    def move_to_formation(self):
        drone_params = self.get_data_from_server("/dronedata", {'droneID': '1'})
        droneLat = float(drone_params['latitude'])  # would be better to just get the location object...
        droneLon = float(drone_params['longitude'])
        droneAlt = float(drone_params['altitude'])

        if (self.formation == "triangle"):

            if (self.id == "1"):
                # Master, so take point
                pass

            elif (self.id == "2"):
                # Slave 1, so take back-left
                # print("Drone 2 Moving To Position")
                self.vehicle.simple_goto(droneLat - .0000018, droneLon - .0000018, droneAlt)
                # print("Master loc:",droneLat,",",droneLon,",",droneAlt)
                self.logger.info("My Loc:" + str(self.vehicle.location.global_relative_frame.lat) + "," + str(
                    self.vehicle.location.global_relative_frame.lon) + "," + str(
                    self.vehicle.location.global_relative_frame.alt))

            elif (self.id == "3"):
                # Slave 2, so take back-right
                # print("Drone 3 Moving To Position")
                self.vehicle.simple_goto(droneLat - .0000018, droneLon + .0000018, droneAlt)

                # print("Master loc:",droneLat,",",droneLon,",",droneAlt)
                self.logger.info("My Loc:" + str(self.vehicle.location.global_relative_frame.lat) + "," + str(
                    self.vehicle.location.global_relative_frame.lon) + "," + str(
                    self.vehicle.location.global_relative_frame.alt))

            else:
                self.logger.info("Cannot Position This Drone In Formation")

        # Add more else if for more formation types

        else:
            self.logger.info("No such formation: " + self.formation)

    def move_to_position(self, lat, lon, alt):
        location = LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(location)

    def follow_in_formation(self, droneID):
        # print("ENTERING FORMATION:", formationName)
        self.move_to_formation()
        # print("About to Enter Loop:", self.vehicle.mode.name)

    def arm(self):
        self.enable_gps()

        self.logger.info("Basic pre-arm checks")

        while not self.vehicle.is_armable:
            self.logger.info(" Waiting for vehicle to initialize...")
            time.sleep(1)

        self.logger.info("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            self.logger.info("Waiting for arming...")
            self.vehicle.armed = True
            time.sleep(1)

        self.vehicle.add_attribute_listener('location.global_relative_frame', self.location_callback)
        self.vehicle.add_attribute_listener('armed', self.armed_callback)
        self.vehicle.add_attribute_listener('mode', self.mode_callback)

        self.logger.info("Vehicle Armed!")

    def disable_gps(self):  # http://ardupilot.org/copter/docs/parameters.html
        if not self.sitl:  # don't try updating params in sitl cuz it doesn't work. problem on their end
            self.vehicle.parameters["ARMING_CHECK"] = 0
            self.vehicle.parameters["GPS_TYPE"] = 3
            self.vehicle.parameters["GPS_AUTO_CONFIG"] = 0
            self.vehicle.parameters["GPS_AUTO_SWITCH"] = 0
            self.vehicle.parameters["FENCE_ENABLE"] = 0

    def enable_gps(self):  # http://ardupilot.org/copter/docs/parameters.html
        if not self.sitl:
            self.vehicle.parameters["ARMING_CHECK"] = 1
            self.vehicle.parameters["GPS_TYPE"] = 1
            self.vehicle.parameters["GPS_AUTO_CONFIG"] = 1
            self.vehicle.parameters["GPS_AUTO_SWITCH"] = 1
            self.vehicle.parameters["FENCE_ENABLE"] = 0

    def arm_no_GPS(self):

        self.logger.info("Arming motors NO GPS")
        self.vehicle.mode = VehicleMode("SPORT")

        while not self.vehicle.armed:
            self.logger.info(" Waiting for arming...")
            self.disable_gps()
            time.sleep(3)
            self.vehicle.armed = True

        self.send_data_to_server("/dronedata", self.get_drone_data())

    def shutdown(self):
        self.vehicle.remove_attribute_listener('location.global_relative_frame', self.location_callback)
        self.vehicle.remove_attribute_listener('armed', self.armed_callback)
        self.vehicle.remove_attribute_listener('mode', self.mode_callback)
        self.vehicle.close()

    # =================================MISSION FUNCTIONS=====================================================
    # =======================================================================================================
    def wait_for_swarm_ready(self, size):  # THIS FUNCTION IS CURRENTLY MASTER SPECIFIC. ONLY CALL FROM MASTER
        # Will eventually need to change below to wait for each drone in the network to be ready...not just one
        drones = 0
        while (drones < size):
            for i in range(0, size):
                slave_params = self.get_data_from_server("/dronedata", {'droneID': i})
                if slave_params == "NO_DATA":
                    if drones == 0:
                        self.logger.info("No Drones Found in the Swarm.")
                    else:
                        self.logger.info((str)(drones) + " Drone(s) found")
                    self.logger.info("Slave: " + (str)(drones + 1) + " not found in swarm")
                    time.sleep(1)
                else:
                    self.logger.info("Found New Drone!")

        self.logger.info("Found " + (str)(drones) + "Drones in the Swarm.")
        for i in range(i, size):
            swarm_params = self.get_data_from_server("/dronedata", {'droneID': i})
            self.logger.info(swarm_params)

        self.logger.info("Swarm ready!")

    def wait_for_drone_match_altitude(self, droneID):
        drone_params = self.get_data_from_server("/dronedata", {'droneID': droneID})
        while drone_params == "NO_DRONE_DATA":
            self.logger.info("Cannot Find Drone " + str(droneID) + " On The Swarm")
            time.sleep(0.5)
            drone_params = self.get_data_from_server("/dronedata", {'droneID': droneID})

        while float(drone_params["altitude"]) <= float(
                self.get_drone_data()["altitude"] * .95):  # FIGURE OUT HOW TO DEAL IN VALUES NOT STRINGS
            self.logger.info("Drone " + droneID + " Stats: " + drone_params["altitude"])
            drone_params = self.get_data_from_server("/dronedata", {'droneID': droneID})
        self.logger.info("Drone " + droneID + " Has Matched Altitude...")

    def wait_for_swarm_to_match_altitude(self, swarm_size):
        for i in range(0, swarm_size):
            self.logger.info(
                "Waiting for Drone: " + (str)(i) + " to reach " + self.vehicle.location.global_relative_frame.alt)
            self.wait_for_drone_match_altitude(i)

    def wait_for_drone_reach_altitude(self, droneID, altitude):
        drone_params = self.get_data_from_server("/dronedata", {'droneID': droneID})
        while drone_params == "NO_DRONE_DATA":
            self.logger.info("Cannot Find Drone " + str(droneID) + " On The Swarm")
            time.sleep(1)
            drone_params = self.get_data_from_server("/dronedata", {'droneID': droneID})
        self.logger.info("OTHER DRONES PARAMS" + str(drone_params))
        while float(drone_params[
                        "altitude"]) <= altitude * .95:  # FIGURE OUT HOW TO DEAL IN VALUES NOT STRINGS #ADD TRY EXCEPT FOR IF THE DATA CAME BACK AS STRING AND NOT OBJECT
            self.logger.info("Drone " + droneID + " Stats: " + drone_params["altitude"])
            drone_params = self.get_data_from_server("/dronedata", {'droneID': droneID})
        self.logger.info("Drone " + droneID + " Has Reached Altitude...")

    def arm_and_takeoff(self, aTargetAltitude):
        self.arm()

        self.logger.info("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        while True:
            self.logger.info("Vehicle Altitude: " + str(self.vehicle.location.global_relative_frame.alt))
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * .95:
                self.logger.info("Reached target altitude")
                self.send_data_to_server("/dronedata", self.get_drone_data())
                break
            time.sleep(.75)

    def arm_formation(self, droneID):
        # Treat drone droneID as a TREAP for a formation
        drone_params = self.get_data_from_server("/dronedata", {'droneID': '1'})
        self.logger.info("Drone: " + droneID + " Parameters Came Back As: " + drone_params)

        while drone_params == "NO_DRONE_DATA":
            self.logger.info("Drone: " + droneID + "Not Found On Swarm")
            time.sleep(1)
            drone_params = self.get_data_from_server("/dronedata", {'droneID': '1'})

        if drone_params["armed"] == True:
            self.logger.info("Drone : " + drone_params["id"] + " armed status - " + drone_params["armed"])
            self.arm()
        else:
            self.logger.info("Drone : " + drone_params["id"] + " armed status - " + drone_params["armed"])

        self.arm_no_GPS()

    def goto(self):
        pass

    def land_vehicle(self):
        self.logger.info("Returning to Launch!!!")

        if self.sitl:
            self.vehicle.airspeed = 3
        else:
            self.vehicle.parameters["RTL_ALT"] = 0.0
            self.vehicle.airspeed = 1

        self.set_mode("RTL")
        while self.vehicle.mode.name != "RTL":
            self.logger.info("Vehicle Mode Didn't Change")
            self.set_mode("RTL")
            time.sleep(1)
        # http://ardupilot.org/copter/docs/parameters.html#rtl-alt-rtl-altitude
        while self.vehicle.location.global_relative_frame.alt > 0.2:
            self.logger.info("Altitude: " + str(self.vehicle.location.global_relative_frame.alt))
            time.sleep(1)
        self.logger.info("Landed!")

    def autoGoTo(self):
        self.mission.executeAutoGoTo()

    def toString(self):
        return ("id: " + self.id + ", " + "ip" + self.ip + ", " + "self.webserver" + self.webserver)