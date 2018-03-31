import json
import requests
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
#import dronekit_sitl

#--------------------------Functions-----------------------------------
def send_data_to_server(route,data):
    url = "http://localhost:5000"+route
    r = requests.post(url, json.dumps(data))
    #print("\nServer Responded With: ", r.status_code ," ", r.text,"\n")

def get_datafrom_server(route,data):
    url = "http://localhost:5000"+route
    r = requests.get(url, data=data)
    #print("\nServer Responded With: ", r.status_code ," ", r.text,"\n")
    #print("\n\nRETURNING: ",r.text,"\n\n")
    try :
        json_val = json.loads(r.text)
        return json_val
    except:
        return r.text
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    arm()   

    print ("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print (" Altitude: ", vehicle.location.global_relative_frame.alt )
        send_data_to_server("/dronedata", getDroneData())
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*.95: 
            print ("Reached target altitude")
            send_data_to_server("/dronedata", getDroneData())
            break
    time.sleep(.25)
    send_data_to_server("/dronedata", getDroneData())

def getDroneData():
    #creates a dictionary object out of the drone data
    droneData = {
            "id":"1",
            "latitude":str(vehicle.location.global_frame.lat),
            "longitude":str(vehicle.location.global_frame.lon),
            "altitude":str(vehicle.location.global_relative_frame.alt),
            "armed":vehicle.armed
            }
    return droneData

def wait_for_swarm_ready() : 
    #Will eventually need to change below to wait for each drone in the network to be ready...not just one
    slave_params = get_datafrom_server("/dronedata",{'droneID':'2'})
    #print("SLAVE_PARAMS CAME BACK AS: ",slave_params)
    while slave_params == "NO_DATA" :
        print("No Slave Drone Found Registered On Swarm")
        time.sleep(1)
        slave_params = get_datafrom_server("/dronedata", {'droneID':'2'})

    #print("SLAVE_PARAMS CAME BACK AS: ",slave_params)
    while float(slave_params["altitude"]) <= ALT_TO_FLY_TO*.95:   
        print("Other Drones Stats...: ",slave_params["altitude"])
        #make a request to the webserver where each drone should be posting their info
        #if the alt and arm status is good we can break
        slave_params = get_datafrom_server("/dronedata",{'droneID':'2'})
        #time.sleep(.25)
def arm():
    print ("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print (" Waiting for vehicle to initialize...")
        time.sleep(1)

        
    print ("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    
    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print (" Waiting for arming...")
        vehicle.armed = True
        time.sleep(1)
    
def arm_no_GPS():
    
    print ("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    #while not vehicle.is_armable:
    #    print (" Waiting for vehicle to initialize...")
    #    time.sleep(1)
        
    print ("Arming motors")

    vehicle.mode = VehicleMode("SPORT")
    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print (" Waiting for arming...")
        vehicle.parameters["ARMING_CHECK"] = 0
        vehicle.parameters["GPS_TYPE"] = 0
        vehicle.parameters["GPS_AUTO_CONFIG"]=0
        vehicle.parameters["GPS_AUTO_SWITCH"]=0
        vehicle.parameters["FENCE_ACTION"]=0
        vehicle.parameters["FENCE_ENABLE"]=0
        time.sleep(3)
        vehicle.armed = True
    send_data_to_server("/dronedata",getDroneData())
    
def arm_formation():
    master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
    print("MASTER_PARAMS CAME BACK AS: ",master_params)
    
    while master_params == "NO_DATA":
        print("No Master Drone Found Registered On Swarm")
        time.sleep(1)
        master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
        
    if master_params["armed"] == True:
        print ("Drone : ",master_params["id"], " armed status - ", master_params["armed"])
        arm()
    else:
        print ("Drone : ",master_params["id"], " armed status - ", master_params["armed"])
    
    arm()
    
def land_vehicle() :

    vehicle.airspeed = 1
    vehicle.mode = VehicleMode("RTL")
    #http://ardupilot.org/copter/docs/parameters.html#rtl-alt-rtl-altitude
    while vehicle.location.global_relative_frame.alt > 0.2 :
        print("Altitude: ",str(vehicle.location.global_relative_frame.alt))
    print("Landed!")

#-------------------------------------------------------------------------------------

#-----------------------------Configure Sitl & Connect to the Vehicle------------------------------------------
#sitl = dronekit_sitl.start_default(47.9217090,-97.06806340) # basic ArduCopter sim
connection_string = '/dev/ttyACM0'#'tcp:127.0.0.1:5780' #sitl.connection_string()
time.sleep(2)
print ('\nConnecting to vehicle on: %s\n' % connection_string)
vehicle = connect(connection_string, wait_ready=True)
#-------------------------------------------------------------------------------------
#for key, value in vehicle.parameters.iteritems() :
    #print ( "Key: ", key, "Value: ",value)
#---------------------------initialize into the swarm-------------------------------------

print("\nInitializing To The Swarm\n")
send_data_to_server("/",getDroneData()) #Makes an adddrone request

#-------------------------------------------------------------------------------------

#----------------------Vehicle commands/Main Functions-------------------------------


#arm_no_GPS()
vehicle.parameters['RTL_ALT'] = 1500.0
print(vehicle.parameters['RTL_ALT'])
vehicle.parameters['RTL_ALT'] = 300.0
print(vehicle.parameters['RTL_ALT'])
                        
ALT_TO_FLY_TO = 2
arm_and_takeoff(ALT_TO_FLY_TO)

print("\nWaiting For Other Nodes To Arm & Match Altitude...\n")
wait_for_swarm_ready()

print("\n\n\nSwarm ready to go!\n\n\n")
print("Returning to Launch")
land_vehicle()

#print ("Beggining Movement To Waypoint One")
#print ("Set default/target airspeed to 3")
#------------------------------------------------------------------------------------