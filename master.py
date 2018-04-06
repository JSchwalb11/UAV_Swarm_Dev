#=============================master.py===================================================================
# Author: Martin Pozniak, Joseph Schwalb
# Desc: This script controls the behavior of the master drone in flight.
# Creation Date: 12/~/2017
# Latest Functionality: Script is used to takeoff the master and wait for pilot control to demo slaves following master's movements.
#=============================================================================================================
import subprocess
from droneBrain import Drone
import time
import logging
from Logger import getLocalTime

#import netifaces as ni
path = "logs/id:1/"
id = '1'
GLT= getLocalTime(id)
#Logger setup
logger = logging.getLogger("master_log")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(path + GLT.getFile())
fh.setLevel(logging.DEBUG)
#create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
#set format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
#move handlers to logger
logger.addHandler(fh)
logger.addHandler(ch)

ipAddr = "192.168.1.1" # This is set in case you are on windows and the following code can't get the ip dynamically
#============This Can Only Be Done On Linux!!==================
# ni.ifaddresses('wlan0')
# ipAddr = ni.ifaddresses('waln0')[ni.AF_INET][0]['addr']
#==============================================================

#====Set Arg To True For Sitl on Port=====
#====Set To False For Physical Drone======
print("=====================MASTER=======================")
print("==================="+ipAddr+"===================")
drone = Drone(useSitl=false,port="5770",ID=id,ip=ipAddr,logger=logger)

print("Adding Drone To Swarm")
drone.add_to_swarm()

print("Printing The Current Nodes In Swarm")
print("===================================")
print("Swarm:", drone.get_swarm_data())
print("===================================")

#===============MISSION====================
ALT_TO_FLY_TO = 2

#drone.arm_no_GPS()

print("===========TAKING_OFF====================")
drone.arm_and_takeoff(ALT_TO_FLY_TO)
print("=========================================")

print("===========WAITING_FOR_SWARM=============")
# drone.wait_for_drone_match_altitude(droneID='2')
# drone.wait_for_drone_match_altitude(droneID='3')
drone.wait_for_swarm_to_match_altitude()
print("=========================================")

# print("Moving Drone To Somewhere")
# drone.set_airspeed(3)
# drone.move_to_position(47 ,104, 20.0)
# while (1):
# 	data= drone.get_drone_data()
# 	print(data["latitude"]+" - "+data["longitude"]+" - "+data["altitude"])
# 	time.sleep(.75)

print("===========WAITING_FOR_PILOT_TO_TAKE_CONTROL=============")
counter = 0
print("PILOT NOT IN CONTROL")
while (drone.get_drone_data()["mode"] != "ALT_HOLD" and counter < 120): #if pilot doesn't take over in x seconds, it breaks 120 for 30 seconds
    print("Counter: ",counter)
    counter = counter+1
print("=========================================================")

print("===========PILOT_IS_IN_CONTROL=================")
while (drone.get_drone_data()["mode"] == "ALT_HOLD"):
    time.sleep(.25)
print("=========================================")

print("===========SCRIPT_TAKING_CONTROL_WAITING_FOR_DRONE_TO_ENTER_GUIDED_MODE=================")
counter = 0

while (drone.get_drone_data()["mode"] != "GUIDED" and counter < 20): #if vehicle mode doesn't switch within x seconds move on to the land and shutdown which should also attempt to switch to guided.
    print("Counter: ",counter)    
    counter= counter + 1
    print("Forcing Guided Mode")
    drone.set_mode("GUIDED")
    time.sleep(.25)
print("===============================================================")

print("===========DRONE_LANDING=================")
drone.land_vehicle()
print("=========================================")

print("===========SHUTTING_DOWN=================")
drone.shutdown()
print("=========================================")
