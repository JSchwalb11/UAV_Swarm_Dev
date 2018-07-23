import json
import logging
from config import Config
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
from pymavlink import mavutil
import GISUtils
from droneData2 import assert_true
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
        self.webserver = str(self.ip) + ":" + str(self.default_webserver_port)
        self.connection_string = '/dev/ttyACM0'

        if self.sitl:
            self.sitl_instance = self.sitl_setup()
            self.connection_string = self.sitl_instance.connection_string()

        self.logger = logging.getLogger("drone" + str(self.id) + "_log")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler("drone" + str(self.id) + "_log")
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.csv_logger = logging.getLogger("drone" + str(self.id) + "_csv")
        self.csv_logger.setLevel(logging.INFO)
        fh = logging.FileHandler("drone" + str(self.id) + "_csv")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        self.csv_logger.addHandler(fh)

        self.vehicle = connect(self.connection_string)
        print("Drone: " + str(self.id) + " connected!")
        self.drone_data = self.get_drone_data()
        self.vehicle.commands.clear()
        print("Waiting for vehicle to clear commands!")
        self.vehicle.commands.wait_ready()
        print("Done clearing commands!")


        print('\nConnecting to vehicle on: %s\n' % self.connection_string)
        # Always add the drone to swarm last.

    def sitl_setup(self):
        from dronekit_sitl import SITL
        instance = self.id - 1
        sitl_instance = SITL(instance=instance)
        sitl_instance.download('copter', '3.3', verbose=True)
        # system (e.g. "copter", "solo"), version (e.g. "3.3"), verbose

        sitl_args = ['--model', 'quad', '--home=' + str(self.home_location.lat) + "," +
                                                    str(self.home_location.lon) + "," +
                                                    str(self.home_location.alt) + ",360"]

        sitl_instance.launch(sitl_args, verbose=False, await_ready=True, restart=True)

        return sitl_instance

    def get_state(self):
        """
        This function returns the state of the vehicle (or autopilot capabilities [vehicle_state.py]) as a string in CSV format.

        The returning CSV string is formatted as below:
            Types are included in this description for debugging purposes, but not included as part of the return statement.

            Ex. output:
                value0, value1, [...], value33 + '\n'

            ASCTime ASCTime of log
            Boolean Supports MISSION_FLOAT
            Boolean Supports PARAM_FLOAT
            Boolean Supports MISSION_INT
            Boolean Supports COMMAND_INT
            Boolean Supports PARAM_UNION
            Boolean Supports ftp for file transfers
            Boolean Supports commanding attitude offboard
            Boolean Supports commanding position and velocity targets in local NED frame
            Boolean Supports set position + velocity targets in global scaled integers
            Boolean Supports terrain protocol / data handling
            Boolean Supports direct actuator control
            Boolean Supports the flight termination command
            Boolean Supports onboard compass calibration
            LocationGlobal Global Location
            LocationGlobalRelative Global Location (relative altitude)
            LocationLocal Local Location
            Attitude Attitude
            List[x,y,z] Velocity
            GPSInfo GPS
            Gimbal Gimbal status
            Battery Battery
            Boolean EKF OK?
            Float Last Heartbeat
            Rangefinder Rangefinder
            Rangefinder Rangefinder distance
            Rangefinder Rangefinder voltage
            Int Heading
            Boolean Is Armable?
            SystemStatus System status
            Double Groundspeed
            Double Airspeed
            String Mode
            Boolean Armed

        :return:
        """
        string = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                  time.time(),
                  self.vehicle.capabilities.mission_float,
                  self.vehicle.capabilities.param_float,
                  self.vehicle.capabilities.mission_int,
                  self.vehicle.capabilities.command_int,
                  self.vehicle.capabilities.param_union,
                  self.vehicle.capabilities.ftp,
                  self.vehicle.capabilities.set_attitude_target,
                  self.vehicle.capabilities.set_attitude_target_local_ned,
                  self.vehicle.capabilities.set_altitude_target_global_int,
                  self.vehicle.capabilities.terrain,
                  self.vehicle.capabilities.set_actuator_target,
                  self.vehicle.capabilities.flight_termination,
                  self.vehicle.capabilities.compass_calibration,
                  self.vehicle.location.global_frame.lat,
                  self.vehicle.location.global_frame.lon,
                  self.vehicle.location.global_frame.alt,
                  self.vehicle.location.global_relative_frame.alt,
                  self.vehicle.location.local_frame,
                  self.vehicle.attitude,
                  self.vehicle.velocity,
                  self.vehicle.gps_0,
                  self.vehicle.gimbal,
                  self.vehicle.battery,
                  self.vehicle.ekf_ok,
                  self.vehicle.last_heartbeat,
                  self.vehicle.rangefinder,
                  self.vehicle.rangefinder.distance,
                  self.vehicle.rangefinder.voltage,
                  self.vehicle.heading,
                  self.vehicle.is_armable,
                  self.vehicle.system_status.state,
                  self.vehicle.groundspeed,
                  self.vehicle.airspeed,
                  self.vehicle.mode.name,
                  self.vehicle.armed
                  )
        return string

    def location_callback(self, vehicle, attr_name, value):
        self.logger.debug(value)
        self.csv_logger.info(self.get_state())
        self.update_self_to_swarm("/Swarm")
        if self.vehicle.location.global_relative_frame.alt < 2 and self.vehicle.mode.name == "GUIDED":  # if the vehicle is in guided mode and alt is less than 2m slow it the f down
            self.vehicle.airspeed = .2

    def armed_callback(self, vehicle, attr_name, value):
        self.logger.debug(msg=(str(attr_name) + ":" + str(value)))
        self.csv_logger.info(self.get_state())
        self.update_self_to_swarm("/Swarm")

    def mode_callback(self, vehicle, attr_name, value):
        self.logger.debug(msg=(str(attr_name) + ":" + str(value)))
        self.csv_logger.info(self.get_state())
        self.update_self_to_swarm("/Swarm")

    # =============================COMMUNICATION TO SERVER===================================================
    # =======================================================================================================

    def update_self_to_swarm(self, route):
        url = 'http://' + self.webserver + route + "?id=" + str(self.id)
        data = self.get_drone_data().__dict__[(str(self.id))]
        try:
            r = requests.put(url, json=data)
            self.logger.debug("\nServer Responded With: " + str(r.status_code) + " " + str(r.text) + "\n")
            return r.status_code
        except requests.HTTPError:
            self.logger.info(str(requests.HTTPError))
            return r.status_code

    def get_data_from_server(self, route):
        url = 'http://' + self.webserver + route  # + "/" + str(self.id)  # + "/" + str(self.id)
        try:
            r = requests.get(url)
            json_data = json.loads(r.text)
            parsed_data = Config(json_data)
            return parsed_data
        except requests.HTTPError:
            return r.status_code

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

    def follow_in_formation(self, formation, formationAlt, bool):
        self.goto_formation(formation=formation, formationAltitude=formationAlt, bool=bool)

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
        # self.vehicle.add_attribute_listener('armed', self.armed_callback)
        # self.vehicle.add_attribute_listener('mode', self.mode_callback)

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
        # self.vehicle.remove_attribute_listener('location.global_relative_frame', self.location_callback())
        # self.vehicle.remove_attribute_listener('armed', self.armed_callback())
        # self.vehicle.remove_attribute_listener('mode', self.mode_callback())
        self.vehicle.close()

    # =================================MISSION FUNCTIONS=====================================================
    # =======================================================================================================

    def wait_for_drone_match_altitude(self, droneID):
        self.wait_for_drone_reach_altitude(droneID, self.vehicle.location.global_relative_frame.alt)

    def wait_for_swarm_to_match_altitude(self):
        swarm_params = self.get_data_from_server("/Swarm")

        for idx, drones in enumerate(swarm_params.Drones):
            self.wait_for_drone_match_altitude(idx)

    def wait_for_drone_reach_altitude(self, droneID, altitude):
        swarm_params = self.get_data_from_server("/Swarm")

        for idx, drone in enumerate(swarm_params.Drones):
            if int(swarm_params.Drones[idx].id) == droneID:
                while (swarm_params.Drones[idx].altitude <= altitude * 0.95):
                    swarm_params = self.get_data_from_server("/Swarm")
                    print("Waiting for Drone: " + str(swarm_params.Drones[idx].id) + " to reach " + str(
                        altitude))
                    time.sleep(1)
                self.logger.info(
                    "Drone: " + swarm_params.Drones[idx].id + " reached " + str(altitude) + "...")

    def watch_leader_mode(self, drone_id):
        data = self.get_data_from_server("/Swarm")
        leader_idx = 0
        for idx, drone in enumerate(data.Drones):
            if drone.id == drone_id:
                leader_idx = idx

        leader_mode = data.Drones[leader_idx].mode
        return leader_mode

    def wait_for_swarm_ready(self, expected_swarm_size):
        # drone_data.Drones[drone_id][1 (indexing bug)].get("ip")
        swarm_ready_status = []

        while not assert_true(swarm_ready_status):
            swarm_params = self.get_data_from_server("/Swarm")
            actual_swarm_size = swarm_params.Drones.__len__()
            print("Found " + str(actual_swarm_size) + "Drones in the Swarm.")
            if expected_swarm_size == actual_swarm_size:
                for idx, drone in enumerate(swarm_params.Drones):
                    if not swarm_params:
                        print("No Drones Found in the Swarm.")
                    else:
                        if not swarm_params.Drones[idx]:
                            print("No Drones Found in the Swarm.")
                        else:
                            print("Drone: " + str(swarm_params.Drones[idx].id) + " found in swarm")
                            swarm_ready_status.append(1)
                            time.sleep(1)
                assert_true(swarm_ready_status)
        # if swarm_is_not_ready and all drones have been checked, do loop again
        print("Swarm is ready!")

    def goto_formation(self, formation, formationAltitude, bool):
        # Formation on X,Y axes

        swarm_data = self.get_data_from_server("/Swarm")
        # Form up on first drone in swarm for now
        head_drone_data = swarm_data.Drones[0]
        head_drone_loc = LocationGlobalRelative(float(head_drone_data.latitude), float(head_drone_data.longitude),
                                                float(head_drone_data.altitude))

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
            if self.id == 1:
                self.vehicle.simple_goto(
                    LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon), formationAltitude))

            elif self.id == 2:

                # Maneuver 5 metres below formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude - 5

                dEast = 3
                dNorth = -3

                target_loc = GISUtils.get_location_coord(head_drone_loc, dNorth=dNorth, dEast=dEast)
                GISUtils.goto(self, target_loc, dNorth=dNorth, dEast=dEast)

                """
                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat) - .0000027,
                                                   float(head_drone_loc.lon) - 0.0000027, safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat) - .0000027,
                                                   float(head_drone_loc.lon) - 0.0000027, formationAltitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                """


            elif self.id == 3:

                # Maneuver 5 metres above formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude + 5

                dEast = -3 #positive for east, negative for west
                dNorth = -3 # positive for north, negative for south

                target_loc = GISUtils.get_location_coord(head_drone_loc, dNorth=dNorth, dEast=dEast)
                GISUtils.goto(self, target_loc, dNorth=dNorth, dEast=dEast)

                """
                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat) + .0000027,
                                                   float(head_drone_loc.lon) - 0.0000027, safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat) + .0000027,
                                                   float(head_drone_loc.lon) - 0.0000027, formationAltitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                """

            else:
                self.logger.info("Something weird happened...")

        elif formation == "stacked":
            """
            # Special formation altitude represents the separation on the Z axis between the drones
            #fix stacked
            special_formation_altitude = 3

            if self.id == 1:

                # Maneuver to formation altitude
                self.vehicle.simple_goto(float(head_drone_loc.lat), float(head_drone_loc.lon), formationAltitude)

            elif self.id == 2:

                # Maneuver 5 metres below formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude - 5

                dEast = -5 #positive for east, negative for west
                dNorth = -5 # positive for north, negative for south

                current_loc = self.vehicle.location.global_relative_frame
                target_loc = head_drone_loc
                GISUtils.goto(self, dNorth=dNorth, dEast=dEast)

                while head_drone_data.mode == 'GUIDED':
                    remainingDist = GISUtils.get_distance_metres(current_loc, target_loc)
                    self.logger.info("%s metres away from leader (ID: %s)...", remainingDist, head_drone_data.id)
                
                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon), safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon),
                                                   formationAltitude - special_formation_altitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                
                
            elif self.id == 3:

                # Maneuver 5 metres above formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude + 5
                
                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon), safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon),
                                                   formationAltitude + special_formation_altitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                
            """
        elif formation == "xaxis":
            if self.id == 1:

                # Maneuver to formation altitude
                self.vehicle.simple_goto(float(head_drone_loc.lat), float(head_drone_loc.lon), formationAltitude)

            elif self.id == 2:

                # Maneuver 5 metres below formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude - 5

                dEast = 5
                dNorth = -5

                target_loc = GISUtils.get_location_coord(head_drone_loc, dNorth=dNorth, dEast=dEast)
                GISUtils.goto(self, target_loc, dNorth=dNorth, dEast=dEast)

                """
                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat) - .0000027, float(head_drone_loc.lon),
                                                   safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat) - .0000027, float(head_drone_loc.lon),
                                                   formationAltitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                """

            elif self.id == 3:

                # Maneuver 5 metres above formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude + 5

                dEast = 5
                dNorth = -5

                target_loc = GISUtils.get_location_coord(head_drone_loc, dNorth=dNorth, dEast=dEast)
                GISUtils.goto(self, target_loc, dNorth=dNorth, dEast=dEast)

                """

                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat) + .0000027, float(head_drone_loc.lon),
                                                   safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat) + .0000027, float(head_drone_loc.lon),
                                                   formationAltitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                """

        elif formation == "yaxis":
            if self.id == 1:

                # Maneuver to formation altitude
                self.vehicle.simple_goto(float(head_drone_loc.lat), float(head_drone_loc.lon), formationAltitude)

            elif self.id == 2:

                # Maneuver 5 metres below formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude - 5

                dEast = 5
                dNorth = -5

                target_loc = GISUtils.get_location_coord(head_drone_loc, dNorth=dNorth, dEast=dEast)
                GISUtils.goto(self, target_loc, dNorth=dNorth, dEast=dEast)

                """
                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon) - .0000027,
                                                   safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon) - .0000027,
                                                   formationAltitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                """
            elif self.id == 3:

                # Maneuver 5 metres above formation altitude
                if bool:
                    safeAltitude = formationAltitude
                elif not bool:
                    safeAltitude = formationAltitude + 5

                dEast = 5
                dNorth = -5

                target_loc = GISUtils.get_location_coord(head_drone_loc, dNorth=dNorth, dEast=dEast)
                GISUtils.goto(self, target_loc, dNorth=dNorth, dEast=dEast)

                """
                waypoint1 = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                   self.vehicle.location.global_relative_frame.lon, safeAltitude)
                waypoint2 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon) + .0000027,
                                                   safeAltitude)
                waypoint3 = LocationGlobalRelative(float(head_drone_loc.lat), float(head_drone_loc.lon) + .0000027,
                                                   formationAltitude)

                while not self.over_3D_fix(waypoint1.lat, waypoint1.lon, waypoint1.alt):
                    self.vehicle.simple_goto(waypoint1)
                while not self.over_3D_fix(waypoint2.lat, waypoint2.lon, waypoint2.alt):
                    self.vehicle.simple_goto(waypoint2)
                while not self.over_3D_fix(waypoint3.lat, waypoint3.lon, waypoint3.alt):
                    self.vehicle.simple_goto(waypoint3)
                """

    def wait_for_next_formation(self, seconds):
        for idx in range(0, seconds):
            self.logger.info(
                "Waiting " + str(seconds) + " seconds before next flight formation... " + str(idx + 1) + "/" + str(
                    seconds))
            time.sleep(1)

    def wait_for_formation(self, seconds):
        for idx in range(0, seconds):
            self.logger.info("Waiting for drones to form up... " + str(idx + 1) + "/" + str(seconds))
            time.sleep(1)

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

    def find_drone_idx(self, drone_id):
        for idx, drone in enumerate(self.get_data_from_server("/Swarm").Drones):
            if (drone.id == drone_id):
                return idx

    def wait_for_leader_takeoff(self, drone_id):
        while not (self.watch_leader_mode(drone_id=drone_id) == 'GUIDED'):
            self.logger.info("Waiting for leader to change modes...")

        data = self.get_data_from_server("/Swarm")
        idx = self.find_drone_idx(1)
        self.logger.info("Flying to: %s, %s, %s", str(data.Drones[idx].latitude), str(data.Drones[idx].longitude),
                         str(data.Drones[idx].altitude))
        self.vehicle.commands.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                    0, 0, 0, 0, 0, 0,
                    data.Drones[0].latitude, data.Drones[0].longitude, data.Drones[0].altitude))
        self.vehicle.commands.upload()
        self.vehicle.commands.wait_ready()

    def arm_and_takeoff(self, aTargetAltitude):

        # Arms vehicle and fly to aTargetAltitude.

        self.logger.info("Basic pre-arm checks")
        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            self.logger.info(" Waiting for vehicle to initialize...")
            # self.vehicle.gps_0.fix_type.__add__(2)
            # self.vehicle.gps_0.__setattr__(self.vehicle.gps_0.fix_type, 3)
            self.logger.debug("Fix type (1-3): " + str(self.vehicle.gps_0.fix_type))
            self.logger.debug("Satellites Visible: " + str(self.vehicle.gps_0.satellites_visible))
            time.sleep(2)

            self.logger.info("Arming motors")

        self.vehicle.add_attribute_listener('location.global_relative_frame', self.location_callback)
        self.vehicle.add_attribute_listener('armed', self.armed_callback)
        self.vehicle.add_attribute_listener('mode', self.mode_callback)

        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            self.logger.info(" Waiting for arming...")
            time.sleep(1)

        self.logger.info("Taking off! " + "(" + str(aTargetAltitude) + ")")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        while self.vehicle.location.global_relative_frame.alt < aTargetAltitude * 0.95:
            self.logger.info(" Currently flying... Alt: " + str(self.vehicle.location.global_relative_frame.alt))
            time.sleep(1)

        if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            self.logger.info("Reached target altitude")

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

    def distance_to_next_waypoint_3d(self):
        x = self.vehicle.location.global_relative_frame.lat - self.vehicle.commands.next

    def over_3D_fix(self, lat, lon, alt):
        # Negate to make sense in english
        # Should be True,False,False
        loc = LocationGlobalRelative(float(lat), float(lon), float(alt))
        if abs(self.vehicle.location.global_frame.lat - loc.lat) < 0.000005:  # 0.000009 ~~ 1 metre
            if abs(self.vehicle.location.global_frame.lon - loc.lon) < 0.000005:  # 0.000009 ~~ 1 metre
                if abs(self.vehicle.location.global_relative_frame.alt - loc.alt) < (loc.alt * 0.05):
                    return True
                return False
            return False
        return False


def toJson(value):
    return {value.__name__() + ":" + value}
