from dronekit import LocationGlobalRelative

import GISUtils
from droneBrain2 import Drone
from config import load_json_config
import time

start_time = time.time()
swarm_cfg = load_json_config("swarm_config")
drone = Drone(swarm_cfg.Drones[1])
drone.update_self_to_swarm('/Swarm')

formationList = ["triangle", "xaxis", "yaxis", "stacked"]
formationAlt = 15.0

"""
drone.vehicle.commands.clear()

drone.vehicle.commands.add(
    Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, 0, formationAlt))
drone.vehicle.commands.add(
    Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_CONDITION_DISTANCE,
            0, 0, 0, 0, 0, 0, 0, 0, formationAlt))

for lap in range(0, 2):
    for idx in range(1, 4):
        drone.vehicle.commands.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                    0, 0, 0, 0, 0, 0, waypoints.get("lat" + str(idx)), waypoints.get("lon" + str(idx)), formationAlt))

drone.vehicle.commands.upload()
drone.vehicle.commands.wait_ready()

drone.vehicle.mode.name = 'AUTO'
"""

drone.wait_for_swarm_ready(3)
drone.arm_and_takeoff(formationAlt)

print("Set groundspeed to 5m/s.")
drone.vehicle.groundspeed = 5
bool = False

while drone.watch_leader_mode(drone_id=1) == 'GUIDED':
    target_loc = LocationGlobalRelative(float(drone.get_data_from_server("/Swarm").Drones[0].latitude),
                                        float(drone.get_data_from_server("/Swarm").Drones[0].longitude),
                                        float(drone.get_data_from_server("/Swarm").Drones[0].altitude))
    remainingDist = GISUtils.get_distance_metres(drone.vehicle.location.global_relative_frame, target_loc)
    drone.logger.info("%s metres away from leader (ID: %s)...", remainingDist,
                    drone.get_data_from_server("/Swarm").Drones[0].id)
    drone.follow_in_formation(formationList[0], formationAlt, bool)
    #stuck following master because it will never get to the exact position
    #need to add estimate
    drone.logger.info("Currently Following...")
    drone.logger.info("Following Leader (%s,%s,%s)", drone.get_data_from_server("/Swarm").Drones[0].latitude,
                      drone.get_data_from_server("/Swarm").Drones[0].longitude,
                      drone.get_data_from_server("/Swarm").Drones[0].altitude)

drone.land_vehicle()
drone.logger.info("Total time: %s", time.time()-start_time)
drone.shutdown()


