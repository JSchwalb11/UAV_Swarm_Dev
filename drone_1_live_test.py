from droneBrain2 import Drone
from config import load_json_config
import GISUtils
import time

swarm_cfg = load_json_config("swarm_config")
drone = Drone(swarm_cfg.Drones[0])
drone.update_self_to_swarm('/Swarm')
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
start_time = time.time()

drone.wait_for_swarm_ready(3)
drone.arm_and_takeoff(formationAlt)
drone.wait_for_swarm_to_match_altitude()

print("Set groundspeed to 3m/s.")
drone.vehicle.groundspeed = 2

lapstart = time.time()
GISUtils.goto(drone=drone, target_loc=GISUtils.get_location_metres(drone.vehicle.location.global_relative_frame, dNorth=-15, dEast=0), dNorth=-15, dEast=0)
GISUtils.goto(drone=drone, target_loc=GISUtils.get_location_metres(drone.vehicle.location.global_relative_frame, dNorth=0, dEast=15), dNorth=0, dEast=15)
GISUtils.goto(drone=drone, target_loc=GISUtils.get_location_metres(drone.vehicle.location.global_relative_frame, dNorth=15, dEast=0), dNorth=15, dEast=0)
GISUtils.goto(drone=drone, target_loc=GISUtils.get_location_metres(drone.vehicle.location.global_relative_frame, dNorth=0, dEast=-15), dNorth=0, dEast=-15)
drone.logger.info("Lap %s complete!", 1)
drone.logger.info("Lap time = %s", (time.time() - lapstart))


drone.land_vehicle()
drone.logger.info("Total time: %s", time.time()-start_time)
drone.shutdown()

