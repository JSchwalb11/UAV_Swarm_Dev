import site
from dronekit import connect, VehicleMode, LocationGlobalRelative
print(site.USER_SITE)
import time

import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.basic_takeoff.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None
connection_string1 = None
connection_string2 = None

if not connection_string:
    from dronekit_sitl import SITL
    print(site.USER_SITE)
    sitl1 = SITL()
    sitl1.download('copter', '3.3', verbose=True)
    sitl2 = SITL()
    sitl2.download('copter', '3.3', verbose=True)
    sitl_args1 = ['-I0', '--simin=127.0.0.1:4000', '--simout=127.0.0.1:4001', '--model',
                         'quad']
    sitl_args2 = ['-I1', '--simin=127.0.0.1:4000', '--simout=127.0.0.1:4001', '--model',
                         'quad']
    sitlInstance1 = sitl1.launch(sitl_args1, verbose=False, await_ready=False, restart=True)
    sitlInstance2 = sitl2.launch(sitl_args2, verbose=False, await_ready=False, restart=True)
    #    sitl = dronekit_sitl.start_default()
    connection_string1 = sitl1.connection_string()
    connection_string2 = sitl2.connection_string()

print('Connecting to vehicle1 on: %s' % connection_string1)
vehicle1 = connect(connection_string1, wait_ready=True)

print('Connecting to vehicle2 on: %s' % connection_string2)
vehicle2 = connect(connection_string2, wait_ready=True)


def arm_and_takeoff(vehicle, aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialize...")
        time.sleep(2)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    while vehicle.location.global_relative_frame.alt < aTargetAltitude * 0.95:
        print(" Currently flying... Alt: ", vehicle.location.global_relative_frame.alt)
        time.sleep(1)

    if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")

arm_and_takeoff(vehicle1, 10)
arm_and_takeoff(vehicle2, 10)