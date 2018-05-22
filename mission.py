from __future__ import division
from dronekit import LocationGlobalRelative, VehicleMode, LocationGlobal, Command
import time
import math
from pymavlink import mavutil



class Mission():

    def __init__(self, vehicle):
        self.mission = []
        self.missionQueue = 0
        self.waypoints = LocationGlobalRelative([], [], [])
        self.waypointsQueue = 0
        self.vehicle = vehicle


    """    
    def formation(self, formation):
        print("Flying in formation... " + formation)
    """
    def distance(self):
        earth_radius = 6378137.0
        print(str(self.vehicle.commands.next) + " test command.next value")
        dLat = (math.pi/180) * (self.waypoints.lat[self.vehicle.commands.next-1] - self.vehicle.location.global_relative_frame.lat)
        dlon = (math.pi/180) * (self.waypoints.lon[self.vehicle.commands.next-1] - self.vehicle.location.global_relative_frame.lon)

        startLat = (math.pi/180) * (self.vehicle.location.global_relative_frame.lat)
        endLat = (math.pi/180) * (self.vehicle.location.global_relative_frame.lon)

        a = self.haversin(dLat) + math.cos(startLat) * math.cos(endLat) * self.haversin(dlon)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius * c

    def get_location_metres(self, dNorth, dEast):
        current_location = self.vehicle.location.global_relative_frame
        #print(str(current_location.lat) + " " + str(current_location.lon) + " " + str(current_location.alt))
        earth_radius = 6378137.0  # Radius of "spherical" earth
        # Coordinate offsets in radians
        dLat = dNorth / earth_radius
        dLon = dEast / (earth_radius * math.cos(math.pi * current_location.lat / 180))

        # New position in decimal degrees
        newlat = current_location.lat + (dLat * 180 / math.pi)
        newlon = current_location.lon + (dLon * 180 / math.pi)
        return LocationGlobal(newlat, newlon, current_location.alt)

    def download_mission(self):
        cmds = self.vehicle.commands
        cmds.download()
        cmds.wait_ready()

    def add_mission(self, size):
        cmds = self.vehicle.commands

        print("Clearing any existing commands")
        cmds.clear()
        print("Commands Cleared!")

        point1 = self.get_location_metres(size, -size)
        point2 = self.get_location_metres(size, size)
        point3 = self.get_location_metres(-size, size)
        point4 = self.get_location_metres(-size, -size)

        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,
                    0, 0, 0, 0, point1.lat, point1.lon, 11))
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,
                    0, 0, 0, 0, point2.lat, point2.lon, 12))
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,
                    0, 0, 0, 0, point3.lat, point3.lon, 13))
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,
                    0, 0, 0, 0, point4.lat, point4.lon, 14))
        # add dummy waypoint "5" at point 4 (lets us know when have reached destination)
        cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,
                    0, 0, 0, 0, point4.lat, point4.lon, 14))

        print("Uploading new commands to vehicle")
        cmds.upload()

    def haversin(self, value):
        return math.pow(math.sin(value / 2), 2)

    def newWaypoint(self, location):
        self.waypoints = []
        self.waypoints += LocationGlobalRelative(location)

    def getCurrentWaypoint(self):
        return self.waypoints[self.waypointsQueue]

    def getNextWaypoint(self):
        return self.waypoints[self.waypointsQueue+1]

    def setNextWaypoint(self, location):
        self.waypoints.insert(self.waypointsQueue+1,location)

    def newMission(self, mission):
        self.mission = []
        self.mission += mission

    def getCurrentMission(self):
        return self.mission[self.missionQueue]

    def getNextMission(self):
        return self.mission[self.missionQueue+1]

    def setNextMission(self,mission):
        self.mission.insert(self.missionQueue+1, mission)

    def autopilot(self):
        print("Starting mission")
        self.vehicle.commands.next = 0

        self.vehicle.mode = VehicleMode("AUTO")

        while True:
            nextwaypoint = self.vehicle.commands.next
            print('Distance to waypoint (%s): %s' % str(self.distance()))

            if nextwaypoint == 3:  # Skip to next waypoint
                print('Skipping to Waypoint 5 when reach waypoint 3')
                self.vehicle.commands.next = 5
            if nextwaypoint == 5:  # Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
                print("Exit 'standard' mission when start heading to final waypoint (5)")
                break;
            time.sleep(1)

        print('Return to launch')
        self.vehicle.set_mode("RTL")