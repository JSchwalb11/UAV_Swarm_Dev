import json

import logging

from mission import Mission
from dronekit import connect, VehicleMode, LocationGlobalRelative
import site

print(site.USER_SITE)

from dronekit_sitl import SITL
import dronekit_sitl

print(dronekit_sitl.__file__)
from config import Config

import requests
import time


class Drone:

    def __init__(self, config):
        self.default_webserver_ip = config.ip
        self.default_port = config.port
        self.default_webserver_port = config.webport
        self.id = config.id
        self.ip = config.ip
        self.home_location = LocationGlobalRelative(config.lat, config.lon, config.alt)
        self.sitl = config.sitl
        # Follow instructions @ https://github.com/abearman/sparrow-dev/wiki/How-to-use-the-DroneKit-SITL-simulator
        self.instance = self.id - 1
        self.sitlInstance = SITL(instance=self.instance)
        self.sitlInstance.download('copter', '3.2.1',
                                   verbose=True)  # system (e.g. "copter", "solo"), version (e.g. "3.3"), verbose

        if self.sitl:
            sitl_args = ['-I' + str(self.id - 1), '--simin=127.0.0.1:4000', '--simout=127.0.0.1:4001', '--model',
                         'quad', '--home=' + str(self.home_location.lat) + "," + str(self.home_location.lon) + "," + str(self.home_location.alt) + ",360"]
            print(str(sitl_args))
            self.sitlInstance.launch(sitl_args, verbose=False, await_ready=False, restart=True)
            self.connection_string = self.sitlInstance.connection_string()
        else:
            self.connection_string = '/dev/tty/ACM0'

        print("Connection_string: " + self.connection_string)
        self.formation = None
        self.webserver = str(self.ip) + ":" + str(self.default_webserver_port)
        print('\nConnecting to vehicle on: %s\n' % self.connection_string)
        print(site.USER_SITE)
        self.vehicle = connect(self.connection_string)
        print("Drone: " + str(self.id) + " connected!")
        self.drone_data = self.get_drone_data()
        # print(self.drone_data.__dict__.get(str(self.id)))
        # self.print_drone_data()
        self.mission = Mission(self.vehicle)
        # logger config
        self.logger = logging.getLogger("/logs/drone" + (str)(self.id) + "_log")
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

    # =============================ATTRIBUTE LISTENER CALLBACKS==============================================
    # =======================================================================================================
    def location_callback(self):
        self.update_self_to_swarm("/Swarm")
        self.logger.info("Drone Location Changed: " + str(self.vehicle.location.global_relative_frame))
        if (
                self.vehicle.location.global_relative_frame.alt < 2 and self.vehicle.mode.name == "GUIDED"):  # if the vehicle is in guided mode and alt is less than 2m slow it the f down
            self.vehicle.airspeed = .2

    def armed_callback(self):
        self.logger.info("Drone Armed Status Changed: " + str(self.vehicle.armed))
        self.update_self_to_swarm("/Swarm")

    def mode_callback(self):
        self.logger.info("Mode Changed: " + str(self.vehicle.mode.name))
        self.update_self_to_swarm("/Swarm")

    # =============================COMMUNICATION TO SERVER===================================================
    # =======================================================================================================

    def update_self_to_swarm(self, route):
        # url = 'http://' + self.webserver + route
        url = 'http://' + self.webserver + route + "?id=" + str(self.id)  # + "/" + str(self.id) + "?id=" + str(self.id)
        data = self.get_drone_data().__dict__[(str(self.id))]
        # print("Data to server: " + data)
        try:
            # r = requests.post(url,data)
            r = requests.put(url, json=data)
            self.logger.info("\nServer Responded With: " + str(r.status_code) + " " + str(r.text) + "\n")
        except requests.HTTPError:
            self.logger.info(str(requests.HTTPError))

    def get_data_from_server(self, route):
        url = 'http://' + self.webserver + route  # + "/" + str(self.id)  # + "/" + str(self.id)
        try:
            r = requests.get(url)
            self.logger.info("\nServer Responded With: " + str(r.status_code) + " " + str(r.text) + "\n")
            return r.text
        except requests.HTTPError:
            self.logger.info("HTTP " + str(requests.HTTPError))

    # =============================VEHICLE INFORMATION FUNCTIONS=================================================
    # =======================================================================================================
    def get_drone_data(self):
        # creates a dictionary object out of the drone data
        return type('obj', (object,), {
            str(self.id): {
                "id": self.id,
                "ip": self.ip,
                "airspeed": self.vehicle.airspeed,
                "latitude": self.vehicle.location.global_frame.lat,
                "longitude": self.vehicle.location.global_frame.lon,
                "altitude": self.vehicle.location.global_relative_frame.alt,
                "armable": self.vehicle.is_armable,
                "armed": self.vehicle.armed,
                "mode": self.vehicle.mode.name
            }
        }
                    )

    def print_drone_data(self):
        drone_params = self.get_drone_data().__dict__.get(str(self.id))
        string_to_print = "Drone ID: " + str(drone_params.get("id")) + "\nDrone IP: " + str(
            drone_params.get("ip")) + "\nDrone A/S: " + str(drone_params.get("airspeed")) + "\nDrone Location: (" + str(
            drone_params.get("latitude")) + ", " + str(drone_params.get("longitude")) + ", " + str(
            drone_params.get("altitude")) + ")" + "\nDrone Armed: " + str(
            drone_params.get("armed")) + "\nDrone Mode: " + drone_params.get("mode")
        print(string_to_print)

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

    def move_to_formation(self, aTargetAltitude):
        drone_params = self.get_drone_data()
        droneLat = float(drone_params)  # would be better to just get the location object...
        droneLon = float(drone_params['longitude'])
        droneAlt = float(drone_params['altitude'])

        # Check altitude is 10 metres so we can manuver around eachother

        if aTargetAltitude is 10:

            if (self.formation == "triangle"):

                if (self.id == "1"):
                    # Master, so take point
                    self.vehicle.simple_goto(self.vehicle.location.global_frame.lat,
                                             self.vehicle.location.global_frame.lon, aTargetAltitude)

                elif (self.id == "2"):
                    # Slave 1, so take back-left
                    # print("Drone 2 Moving To Position")
                    self.vehicle.simple_goto(droneLat - .0000018, droneLon - .0000018, aTargetAltitude - 3)
                    # print("Master loc:",droneLat,",",droneLon,",",droneAlt)
                    self.logger.info("My Loc:" + str(self.vehicle.location.global_relative_frame.lat) + "," + str(
                        self.vehicle.location.global_relative_frame.lon) + "," + str(
                        self.vehicle.location.global_relative_frame.alt))

                elif (self.id == "3"):
                    # Slave 2, so take back-right
                    # print("Drone 3 Moving To Position")
                    self.vehicle.simple_goto(droneLat - .0000018, droneLon + .0000018, aTargetAltitude + 3)

                    # print("Master loc:",droneLat,",",droneLon,",",droneAlt)
                    self.logger.info("My Loc:" + str(self.vehicle.location.global_relative_frame.lat) + "," + str(
                        self.vehicle.location.global_relative_frame.lon) + "," + str(
                        self.vehicle.location.global_relative_frame.alt))

                else:
                    self.logger.info("Cannot Position This Drone In Formation")
            # Add more else if for more formation types
            else:
                self.logger.info("No such formation: " + self.formation)

        else:
            print("Invalid formation altitude!")
            print("Please change formation altitude to 10 metres so the drones can manuver around eachother safetly!")

    def follow_in_formation(self, droneID):
        # print("ENTERING FORMATION:", formationName)
        self.move_to_formation(10)
        # print("About to Enter Loop:", self.vehicle.mode.name)

    def arm(self):
        self.enable_gps()

        self.logger.info("Basic pre-arm checks")

        while not self.vehicle.is_armable:
            self.logger.info(" Waiting for vehicle to initialize...")
            time.sleep(1)
        self.vehicle.mode = VehicleMode("GUIDED")

        self.logger.info("Arming motors")
        # Copter should arm in GUIDED mode
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

        self.update_self_to_swarm("/swarm")

    def shutdown(self):
        self.vehicle.remove_attribute_listener('location.global_relative_frame', self.location_callback)
        self.vehicle.remove_attribute_listener('armed', self.armed_callback)
        self.vehicle.remove_attribute_listener('mode', self.mode_callback)
        self.vehicle.close()

    # =================================MISSION FUNCTIONS=====================================================
    # =======================================================================================================

    def wait_for_drone_match_altitude(self, droneID):
        self.wait_for_drone_reach_altitude(droneID, self.vehicle.location.global_relative_frame.alt)

    def wait_for_swarm_to_match_altitude(self):
        swarm_params = self.get_data_from_server("/Swarm")

        for idx in enumerate(swarm_params):
            self.wait_for_drone_match_altitude(idx)

    def wait_for_drone_reach_altitude(self, droneID, altitude):
        swarm_params = self.get_data_from_server("/Swarm")

        for idx in enumerate(swarm_params.Drones):
            if swarm_params.Drones[idx].id == droneID:
                while (swarm_params.Drones[idx].altitude <= altitude * 0.95):
                    swarm_params = self.get_data_from_server("/Swarm")
                    print("Waiting for Drone: " + str(swarm_params.Drones[idx].id) + " to reach " + str(
                        altitude))
                    time.sleep(1)
                self.logger.info("Drone: " + swarm_params.Drones[idx].id + " reached " + str(altitude) + "...")

    """def arm_and_takeoff(self, aTargetAltitude):
        self.arm()

        self.logger.info("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        while True:
            self.logger.info("Vehicle Altitude: " + str(self.vehicle.location.global_relative_frame.alt))
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * .95:
                self.logger.info("Reached target altitude")
                self.update_self_to_swarm("/Swarm")
                break
            time.sleep(.75)
"""

    def arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print("Basic pre-arm checks")
        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialize...")
            #self.vehicle.gps_0.fix_type.__add__(2)
            self.vehicle.gps_0.__setattr__(self.vehicle.gps_0.fix_type, 3)
            time.sleep(2)

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        while self.vehicle.location.global_relative_frame.alt < aTargetAltitude * 0.95:
            print(" Currently flying... Alt: ", self.vehicle.location.global_relative_frame.alt)
            time.sleep(1)

        if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")

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


def toJson(value):
    return {value.__name__() + ":" + value}
