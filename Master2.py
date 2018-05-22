from droneBrain2 import Drone
from dronekit import LocationGlobalRelative
import random

import argparse
parser = argparse.ArgumentParser(description='Example Arguments:\n'
                                             '--connection_string /dev/ttyACM0\n'
                                             '--connection_string tcp:127.0.0.1:5760\n'
                                             '--sitl True'
                                             '--id 1'
                                             '--ip 127.0.0.1')
parser.add_argument('--sitl')
parser.add_argument('--connection_string')
parser.add_argument('--port')
parser.add_argument('--id')
parser.add_argument('--ip')

args = parser.parse_args()

def sitlArgExists():
    if (args.sitl == "True" or args.connection_string == "False"):
        return True
    else:
        print("Invalid sitl argument.")
        return False

def connectionArgExists():
    if (args.connection_string != None):
        return True
    else:
        print("Null connection_string argument.")
        return False

def portArgExists():
    if (args.port != None):
        try:
            if ((int)(args.port) <= 65535 and (int)(args.port) <= 0):
                return True
            else:
                return False
        except ValueError:
            print("Invalid port argument.")
            return False

def idArgExists():
    if (args.id != None):
        try:
            if ((int)(args.id)):
                return True
            else:
                return False
        except ValueError:
            print("Invalid id argument.")
            return False

def ipArgsExists():
    if (args.ip != None):
        return True
    else:
        print("Null ip argument")
        return False

default_connection_string = '127.0.0.1'
default_ip = '192.168.1.1' #change depending on drone's role - 192.168.1.[1-10]
default_port = '5760'

if(sitlArgExists()):
    sitl = args.sitl
else:
    sitl = False

if(connectionArgExists()):
    connection_string = args.connection_string
else:
    print("No connection_string argument.")
    print("Assigning default connection string: " + default_connection_string)
    connection_string = default_connection_string
    print("SITL intializing...")
    sitl = True

if(portArgExists()):
    port = args.port
    connection_string = connection_string + ":" + port
else:
    port = default_port

if(idArgExists()):
    id = args.id
else:
    id = random.randint(100,1000)

if(ipArgsExists()):
    ip = args.ip
else:
    print("Assigning default ip to drone...")
    ip = default_ip



#====================Waypoints====================
lat = []
lat.append(47.919787)
lat.append(47.919909)
lat.append(47.920198)
lat.append(47.920442)
lat.append(47.920609)

lon = []
lon.append(-97.064406)
lon.append(-97.065055)
lon.append(-97.064737)
lon.append(-97.065055)
lon.append(-97.064410)

alt = []
alt.append(15)
alt.append(12)
alt.append(5)
alt.append(12)
alt.append(15)

print("=====================Drone #" + str(id) + "=======================")
print("==================="+default_ip+"===================")






if (sitl):
    import dronekit_sitl
    sitl = dronekit_sitl.start_default(47.920198, -97.064737)
    connection_string = sitl.connection_string()
else:
    connection_string = '/dev/ttyACM0'

drone = Drone(connection_string,'http://localhost',id,ip,True)
drone.add_to_swarm()
drone.arm_and_takeoff(10)
drone.mission.add_mission(50)
drone.mission.autopilot()

#home_location = drone.vehicle.location.global_relative_frame

drone.shutdown()

print("Flight complete!")