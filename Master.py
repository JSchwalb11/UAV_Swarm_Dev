from droneBrain2 import Drone
from config import Config
import random

import argparse

from droneData2 import Swarm

parser = argparse.ArgumentParser(description='Example Arguments:'
                                             '\n--connection_string /dev/ttyACM0'
                                             '\n--instances 1 , enter the total number of drones in the swarm'
                                             '\n--webport 5000'
                                             '\n--port 5760 , this is for the sitl instance'
                                             '\n--sitl True'
                                             '\n--id 1'
                                             '\n--ip 127.0.0.1')
parser.add_argument('--sitl')
parser.add_argument('--instance')
parser.add_argument('--connection_string')
parser.add_argument('--port')
parser.add_argument('--webport')
parser.add_argument('--id')
parser.add_argument('--ip')

args = parser.parse_args()

def sitlArgExists():
    if args.sitl:
        return True
    return False

def instanceExists():
    if args.instance:
        return True
    return False


def connectionArgExists():
    if (args.connection_string != None):
        return True
    print("Null connection_string argument.")
    return False

def portArgExists():
    if args.port:
        if ((int)(args.port) <= 65535 and (int)(args.port) <= 0):
            return True
    return False

def webport_arg_exists():
    if args.webport:
        return True
    return False

def idArgExists():
    if args.id:
        try:
            (int)(args.id)
            return True
        except ValueError:
            print("Invalid id argument.")
            return False

def ipArgsExists():
    if args.ip:
        return True
    return False

def instance_arg_exists():
    if args.instance:
        return True
    return False


default_id = random.randint(1, 10)
default_ip = '127.0.0.1' #change depending on drone's role - 192.168.1.[1-10]
default_port = '5760'
default_webport = '5000'
default_connection_string = default_ip + ":" + default_port
instance = 0
sitl = False
swarm_config = {
    "Swarm": {
        "size": instance,
        "ip": default_ip,
        "webport": default_webport
    },
    "Drones": []
}

if sitlArgExists():
    sitl = args.sitl

if connectionArgExists():
    default_connection_string = args.connection_string

if portArgExists():
    default_port = args.port

if webport_arg_exists():
    default_webport = args.webport

if idArgExists():
    default_id = args.id

if ipArgsExists():
    default_ip = args.ip

for idx in (0, instance):
    drone_config = {
            "id": default_id + idx,
            "ip": default_ip,
            "port": str(int(default_port) + (instance * 10)),
            "sitl": sitl,
            "webport": default_webport
    }

    swarm_config.get('Drones').append((drone_config))

print(swarm_config.get("Drones").__len__())

#swarm_config = Config(swarm_config)

swarm = Swarm(swarm_config.Swarm)

for idx in enumerate(swarm_config.Drones):
    drone = Drone(swarm_config.Drones[idx])
    swarm.add_drone(drone)

print ("Finished!")


"""
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
"""