import site
p = site.USER_SITE
from droneBrain2 import Drone
from config import load_json_config, Config
import time

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

swarm_config = load_json_config('swarm_config')

default_id = 1
default_ip = '127.0.0.1' #change depending on drone's role - 192.168.1.[1-10]
default_port = '5760'
default_webport = '5000'
default_connection_string = default_ip + ":" + default_port
instance = 0
sitl = True

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


formationList = ["triangle", "xaxis", "yaxis", "stacked"]
formationAlt = 15
waypoints = {"lat1": 47.9190654, "lon1": -97.0647079, "lat2": 47.9188605, "lon2": -97.0647106, "lat3": 47.9188623,
             "lon3": -97.0641875, "lat4": 47.9190798, "lon4": -97.0641875}

"""
Initialize drones in the swarm
"""
swarm = Swarm(swarm_config.Swarm)

for idx, drone_cfg in enumerate(swarm_config.Drones):
    drone = Drone(drone_cfg)
    drone.update_self_to_swarm('/Swarm')
    swarm.add_drone(drone)

swarm.list_swarm()
swarm.wait_for_swarm_ready()
swarm.launch_swarm(15)

# Cycle through formations and waypoints
# Move to a different formation each lap
for idx in range(0, 3):
    for idx2, drone in enumerate(swarm.swarm):
        drone.goto_formation(formationList[idx2], formationAlt, False)
        drone.wait_for_formation(30)

    if drone.id == 1:
        drone.vehicle.simple_goto(waypoints.get("lat" + str(idx)), waypoints.get("lon" + str(idx)), formationAlt)
    else:
        while drone.over_fix(waypoints.get("lat" + str(idx)), waypoints.get("lon" + str(idx))):
            drone.goto_formation(formationList[idx], formationAlt, True)
    drone.wait_for_next_formation(30)


drone.land_vehicle()
drone.shutdown()

formationList = ["triangle", "xaxis", "yaxis", "stacked"]
waypoints = {"lat1": 47.9190654, "lon1": -97.0647079, "lat2": 47.9188605, "lon2": -97.0647106, "lat3": 47.9188623,
             "lon3": -97.0641875, "lat4": 47.9190798, "lon4": -97.0641875}
formationAlt = 15
drone.wait_for_swarm_ready()

for idx, drone in enumerate(swarm.swarm):
    drone.arm_and_takeoff(15)
    drone.wait_for_swarm_to_match_altitude()




# Cycle through formations and waypoints
# Move to a different formation each lap


drone.land_vehicle()
drone.shutdown()
"""
for idx in range (0,30):
    print("Waiting for drones to form up... " + str(idx) + "/30")
    time.sleep(1)

swarm.goto_formation("triangle", 15, True)


print(swarm.get("Drones").__len__())
print("Finished!")

"""
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