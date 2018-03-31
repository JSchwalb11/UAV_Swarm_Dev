import json
import requests
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import dronekit_sitl

#--------------------------Functions-----------------------------------
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
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: 
            print ("Reached target altitude")
            send_data_to_server("/dronedata", getDroneData())
            break
    time.sleep(.25)
    send_data_to_server("/dronedata", getDroneData())

def getDroneData():
    #creates a dictionary object out of the drone data
    droneData = {
            "id":"2",
            "latitude":str(vehicle.location.global_frame.lat),
            "longitude":str(vehicle.location.global_frame.lon),
            "altitude":str(vehicle.location.global_relative_frame.alt),
            "armed":vehicle.armed
            }
    return droneData

def wait_for_swarm_ready() :    
    while True:
        print("Other Drones Stats...")
        #make a request to the webserver where each drone should be posting their info
        #if the alt and arm status is good we can break
        time.sleep(1)
    print("Swarm ready to go!")

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

def fly_formation():
    master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
    print("MASTER_PARAMS CAME BACK AS: ",master_params)

    while master_params == "NO_DATA":
        print("No Master Drone Found Registered On Swarm")
        time.sleep(1)
        master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
        
    #print(type(master_params))
    while float(master_params["altitude"]) <= 2*.95:
        print("Waiting For Master To Get To Altitude...: ",master_params["altitude"])
        #time.sleep(.25)
        master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
        
    arm_and_takeoff(float(master_params["altitude"]))

def arm():
    print ("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print (" Waiting for vehicle to initialise...")
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
    #print ("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    #while not vehicle.is_armable:
       # print (" Waiting for vehicle to initialise...")
       # time.sleep(1)
    
    print ("Arming motors")

    vehicle.mode = VehicleMode("SPORT")
    vehicle.armed = True    

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print (" Waiting for arming...")
        vehicle.parameters["ARMING_CHECK"] = 0
        vehicle.parameters["GPS_TYPE"] = 0
        vehicle.parameters["GPS_AUTO_CONFIG"] = 0
        vehicle.parameters["GPS_AUTO_SWITCH"] = 0
        vehicle.parameters["FENCE_ACTION"] = 0
        vehicle.parameters["FENCE_ENABLE"] = 0
        time.sleep(3)
        vehicle.armed = True    
    
def arm_formation():
    master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
    print("MASTER_PARAMS CAME BACK AS: ",master_params)
    
    while master_params == "NO_DATA":
        print("No Master Drone Found Registered On Swarm")
        time.sleep(1)
        master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
        
    while master_params["armed"] != True:
        master_params = get_datafrom_server("/dronedata",{'droneID':'1'})
        print ("Drone : ",master_params["id"], " armed status - ", master_params["armed"])
    
    arm_no_GPS()
    
def land_vehicle() :
    vehicle.airspeed = 1
    vehicle.mode = VehicleMode("RTL")

    while vehicle.location.global_relative_frame.alt > 0.2 :
        print("Altitude: ",str(vehicle.location.global_relative_frame.alt))
    print("Landed!")
#------------------------------------------------------------------------------------

#-----------------------------Configure Sitl & Connect to the Vehicle------------------------------------------
#sitl = dronekit_sitl.start_default(47.9217072,-97.06806358) # basic ArduCopter sim
connection_string = 'tcp:127.0.0.1:5780'#'/dev/ttyACM0' #sitl.connection_string()
time.sleep(2)
print ('\nConnecting to vehicle on: %s\n' % connection_string)
vehicle = connect(connection_string, wait_ready=True)
#-------------------------------------------------------------------------------------

#---------------------------initialize into the swarm-------------------------------------

print("\nInitializing To The Swarm\n")
send_data_to_server("/",getDroneData()) #Makes an adddrone request

#-------------------------------------------------------------------------------------

#----------------------Vehicle commands/Main Functions-------------------------------

#arm_formation() #For Testing Indoors
vehicle.parameters['RTL_ALT']=0

fly_formation() #For Use Outdoors

print("\n\n\nSwarm ready to go!\n\n\n")
#print("Returning to Launch")
land_vehicle()
#------------------------------------------------------------------------------------

