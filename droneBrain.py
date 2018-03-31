#=============================droneBrain.py===================================================================
# Author: Martin Pozniak, Joey Schwalb
# Desc: This class is used to create a drone object in the main scripts ran on the master or slave. 
#       It contains all functions necessary to initialize a drone and control a drone in our swarm.
#       This is the heart of the drone. Things can be cleaned up and made more dynamic later on.
# Creation Date: 12/~/2017
#============================================================================================================= 
from dronekit import connect, VehicleMode, LocationGlobalRelative
import json
import requests
import time
import dronekit_sitl
import logging
#Docs On guided Mode
#http://python.dronekit.io/guide/copter/guided_mode.html

#=============================DRONE CLASS===================================================================
#=========================================================================================================== 
class Drone() :

    #=====================================Globals===========================================================
    #Choices, triangle, right_ech, left_ech
    formation = "triangle"

    #=============================DRONE 'CONSTRUCTOR' FUNCTION==============================================
    #======================================================================================================= 
    def __init__(self,useSitl,port,ID,ip,logger): #Connect to drone and set up listeners
        self.id = ID
        self.sitlRunning = useSitl
        self.ip = ip
        self.logger = logger

        if useSitl:
            connection_string = 'tcp:127.0.0.1:'+port
        else:
            connection_string = '/dev/ttyACM0' # This address is subject to change depending on USB connections

        print ('\nConnecting to vehicle on: %s\n' % connection_string)
        self.vehicle = connect(connection_string, wait_ready=True)

    #=============================ATTRIBUTE LISTENER CALLBACKS==============================================
    #=======================================================================================================
    def location_callback(self, self2, attr_name, value): #value type is dronekit.LocationGlobalRelative
        if True: #Replace tru with a way to check if any values in location object changed
            try:
                self.send_data_to_server("/dronedata", self.get_drone_data())
                alt = self.vehicle.location.global_relative_frame.alt          
                #print("Alt:",alt)
                if(alt < 2 and self.vehicle.mode.name =="GUIDED"): # if the vehicle is in guided mode and alt is less than 2m slow it the f down
                    self.vehicle.airspeed = .2
            except:
                self.logger.info("Error communicating with server")

        else :
            self.logger.info("Location Object Didn't Change")

    def armed_callback(self, self2, attr_name, value):
        self.logger.info ("Armed Status Of Drone: " + value)
        try:
            self.send_data_to_server("/dronedata", self.get_drone_data())
        except:
            self.logger.info("Error communicating with server")

    def mode_callback(self, self2, attr_name, value):
        self.logger.info ("Mode Of Drone: " + str(value))
        try:
            self.send_data_to_server("/dronedata", self.get_drone_data())
        except:
            self.logger.info("Error communicating with server")
                        

    #=============================COMMUNICATION TO SERVER===================================================
    #=======================================================================================================
    def send_data_to_server(self, route, data):
        try:
            if not self.sitlRunning:
                if self.ip != "192.168.1.1" : #IF DRONES IP IS NOT THAT OF THE SERVER, CONTACT THE SERVER IP | <- THIS NEEDS TO BE MORE DYNAMIC
                    url = "http://"+ "192.168.1.1" + ":5000"+ route # THIS WILL CAUSE AN ISSUE IF YOU TRY TO ASSIGN A PI NOT ON 1.1 TO MASTER!!!!
                else:
                    url = "http://localhost:5000"+route
            else:
                url = "http://localhost:5000"+route

            r = requests.post(url, json.dumps(data))
        except:
            self.logger.info("Error Sending Data To The Server, Is It Running?")
        #print("\nServer Responded With: ", r.status_code ," ", r.text,"\n")

    def get_data_from_server(self, route, data):
        try:
            if not self.sitlRunning:
                if self.ip != "192.168.1.1" : #IF DRONES IP IS NOT THAT OF THE SERVER, CONTACT THE SERVER IP | <- THIS NEEDS TO BE MORE DYNAMIC
                    url = "http://"+ "192.168.1.1" + ":5000"+ route # THIS WILL CAUSE AN ISSUE IF YOU TRY TO ASSIGN A PI NOT ON 1.1 TO MASTER!!!!
                else:
                    url = "http://localhost:5000"+route
            else:
                url = "http://localhost:5000"+route

            r = requests.get(url, data=data)

            # used to see how the server is responding. Maybe just print to log and not console
            #self.logger.info("\nServer Responded With: "+ str(r.status_code) + " " + json.dumps(data) + "\n")#dont log it causes useless clutter
            #self.logger.info("\n\nRETURNING: " + json.dumps(data) + "\n\n")

            try :
                json_val = json.loads(r.text)
                return json_val
            except:
                self.logger.info("Failed to Parse Data To Json Object From Server, Check How The Data Is Received") #printed not loggered
                return r.text
        except:
            self.logger.info("Error Getting Data From The Server, Is It Running?") #printed not loggered?

    def add_to_swarm(self):
        self.send_data_to_server("/adddrone", self.get_drone_data())

    def remove_from_swarm(self):
        return self.send_data_to_server("/removedrone", self.get_drone_data())
    
    def get_swarm_data(self):
        return self.get_data_from_server("/swarmdata",None)

    #=============================VEHICLE INFORMATION FUNCTIONS=================================================
    #======================================================================================================= 
    def get_drone_data(self):
        #creates a dictionary object out of the drone data
        droneData = {
                "id":self.id, #Make this dynamic
                "ip:":self.ip,
                "latitude":str(self.vehicle.location.global_frame.lat), #Change from strings to have server handle dronekit objects
                "longitude":str(self.vehicle.location.global_frame.lon),
                "altitude":str(self.vehicle.location.global_relative_frame.alt),
                "armed":self.vehicle.armed,
                "mode":self.vehicle.mode.name
                }
        return droneData

    #=============================VEHICLE CONTROL FUNCTIONS=================================================
    #======================================================================================================= 
    def set_parameter(self, paramName, value): #Sets a specified param to specified value
        self.vehicle.parameters[paramName] = value

    def set_airspeed(self,value):
        self.vehicle.airspeed=value

    def set_mode(self,mode):
        self.vehicle.mode = VehicleMode(mode)

    def set_formation(self, formationName):
        self.formation = formationName

        master_params = self.get_data_from_server("/dronedata", {'droneID':'1'})
        masterLat = float(master_params['latitude']) #would be better to just get the location object...
        masterLon = float(master_params['longitude']) 
        masterAlt = float(master_params['altitude'])

        if ( self.formation == "triangle" ):

            if( self.id == "1" ) :
                #Master, so take point
                pass

            elif( self.id == "2" ) :
                #Slave 1, so take back-left
                # print("Drone 2 Moving To Position")
                self.move_to_position(masterLat - .0000018 ,masterLon - .0000018, masterAlt)
                #print("Master loc:",masterLat,",",masterLon,",",masterAlt)
                self.logger.info("My Loc:" + str(self.vehicle.location.global_relative_frame.lat) + "," + str(self.vehicle.location.global_relative_frame.lon) + "," + str(self.vehicle.location.global_relative_frame.alt))

            elif( self.id == "3" ) :
                #Slave 2, so take back-right
                # print("Drone 3 Moving To Position")
                self.move_to_position(masterLat - .0000018, masterLon + .0000018, masterAlt)
        
                #print("Master loc:",masterLat,",",masterLon,",",masterAlt)
                self.logger.info("My Loc:" + str(self.vehicle.location.global_relative_frame.lat) + "," + str(self.vehicle.location.global_relative_frame.lon) + "," + str(self.vehicle.location.global_relative_frame.alt))

            else:
                self.logger.info("Cannot Position This Drone In Formation")

        else :
            self.logger.info("No such formation: " + formationName)

    def move_to_position(self,lat,lon,alt):
        location = LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(location)

    def follow_in_formation(self,formationName):
        #print("ENTERING FORMATION:", formationName)
        self.set_formation(formationName)
        #print("About to Enter Loop:", self.vehicle.mode.name)                  


    def arm(self):
        self.enable_gps()

        self.logger.info ("Basic pre-arm checks")

        while not self.vehicle.is_armable:
            self.logger.info (" Waiting for vehicle to initialize...")
            time.sleep(1)
            
        self.logger.info ("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        
        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:      
            self.logger.info ("Waiting for arming...")
            self.vehicle.armed = True
            time.sleep(1)

    def disable_gps(self): #http://ardupilot.org/copter/docs/parameters.html
        if not self.sitlRunning: # don't try updating params in sitl cuz it doesn't work. problem on their end
            self.vehicle.parameters["ARMING_CHECK"] = 0
            self.vehicle.parameters["GPS_TYPE"] = 3
            self.vehicle.parameters["GPS_AUTO_CONFIG"]= 0
            self.vehicle.parameters["GPS_AUTO_SWITCH"]= 0
            self.vehicle.parameters["FENCE_ENABLE"]= 0
    
    def enable_gps(self): #http://ardupilot.org/copter/docs/parameters.html
        if not self.sitlRunning:
            self.vehicle.parameters["ARMING_CHECK"] = 1
            self.vehicle.parameters["GPS_TYPE"] = 1
            self.vehicle.parameters["GPS_AUTO_CONFIG"]= 1
            self.vehicle.parameters["GPS_AUTO_SWITCH"]= 1
            self.vehicle.parameters["FENCE_ENABLE"]= 0

    def arm_no_GPS(self):

        self.logger.info ("Arming motors NO GPS")
        self.vehicle.mode = VehicleMode("SPORT")

        while not self.vehicle.armed:      
            self.logger.info (" Waiting for arming...")
            self.disable_gps()
            time.sleep(3)
            self.vehicle.armed = True

        self.send_data_to_server("/dronedata",self.get_drone_data())
    
    def shutdown(self):
        self.vehicle.remove_attribute_listener('location.global_relative_frame', self.location_callback)
        self.vehicle.remove_attribute_listener('armed', self.armed_callback)
        self.vehicle.close()
    
    #=================================MISSION FUNCTIONS=====================================================
    #=======================================================================================================    
    def wait_for_swarm_ready(self) : #THIS FUNCTION IS CURRENTLY MASTER SPECIFIC. ONLY CALL FROM MASTER
        #Will eventually need to change below to wait for each drone in the network to be ready...not just one
        slave_params = self.get_data_from_server("/dronedata",{'droneID':'2'})
        #print("SLAVE_PARAMS CAME BACK AS: ",slave_params)
        while slave_params == "NO_DATA" :
            self.logger.info("No Slave Drone Found Registered On Swarm")
            time.sleep(1)
            slave_params = self.get_data_from_server("/dronedata", {'droneID':'2'})

        #print("SLAVE_PARAMS CAME BACK AS: ",slave_params)
        while float(slave_params["altitude"]) <= 2*.95:   
            self.logger.info("Other Drones Stats...: "+slave_params["altitude"])
            #make a request to the webserver where each drone should be posting their info
            #if the alt and arm status is good we can break
            slave_params = self.get_data_from_server("/dronedata",{'droneID':'2'})
            #time.sleep(.25)

    def wait_for_master_ready(self): #THIS FUNCTION IS CURRENTLY SLAVE SPECIFIC. ONLY CALL FROM SLAVE
        #Will eventually need to change below to wait for each drone in the network to be ready...not just one
        master_params = self.get_data_from_server("/dronedata",{'droneID':'1'})
        #print("MASTER_PARAMS CAME BACK AS: ",master_params)
        while master_params == "NO_DRONE_DATA" :
            self.logger.info("No Master Drone Found Registered On Swarm")
            time.sleep(1)
            master_params = self.get_data_from_server("/dronedata", {'droneID':'1'})

        #print("MASTER_PARAMS CAME BACK AS: ", master_params)
        while float(master_params["altitude"]) <= 2*.95:   
            self.logger.info("Master Drones Stats...: " + str(master_params["altitude"]))
            #if the alt and arm status is good we can break
            master_params = self.get_data_from_server("/dronedata",{'droneID':'1'})
            #time.sleep(.25)
    
    def wait_for_drone_match_altitude(self,droneID):
        other_drone_params = self.get_data_from_server("/dronedata",{'droneID':droneID})
        while other_drone_params == "NO_DRONE_DATA":
            self.logger.info("Cannot Find Drone "+str(droneID)+" On The Swarm")
            time.sleep(1)
            other_drone_params = self.get_data_from_server("/dronedata",{'droneID':droneID})

        while float(other_drone_params["altitude"]) <= .95*float(self.get_drone_data()["altitude"]):#FIGURE OUT HOW TO DEAL IN VALUES NOT STRINGS 
            self.logger.info ("Drone "+droneID+" Stats: " + str(other_drone_params["altitude"]))
            other_drone_params = self.get_data_from_server("/dronedata",{'droneID':droneID})
            #time.sleep(.25)
        self.logger.info("Drone "+droneID+" Has Matched Altitude...")

    def wait_for_swarm_to_match_altitude(self):
        swarmData = self.get_swarm_data()
        self.logger.info("There are " + str(len(swarmData)) +" in the swarm.")
        for drone in swarmData:
            self.logger.info("Waiting for drone "+drone["id"]+" to match altitude")
            self.wait_for_drone_match_altitude(drone["id"])
            self.logger.info("It matched")


    def wait_for_drone_reach_altitude(self,droneID,altitude):
        other_drone_params = self.get_data_from_server("/dronedata",{'droneID':droneID})
        while other_drone_params == "NO_DRONE_DATA":
            self.logger.info("Cannot Find Drone "+str(droneID)+" On The Swarm")
            time.sleep(1)
            other_drone_params = self.get_data_from_server("/dronedata",{'droneID':droneID})
            self.logger.info("OTHER DRONES PARAMS" + str(other_drone_params))
        self.logger.info("OTHER DRONES PARAMS" + str(other_drone_params))
        while float(other_drone_params["altitude"]) <= altitude*.95:#FIGURE OUT HOW TO DEAL IN VALUES NOT STRINGS #ADD TRY EXCEPT FOR IF THE DATA CAME BACK AS STRING AND NOT OBJECT
            self.logger.info("Drone " + str(droneID) +" Stats: " +  str(other_drone_params["altitude"]))
            other_drone_params = self.get_data_from_server("/dronedata" , {'droneID':droneID})
            #time.sleep(.25)
        self.logger.info("Drone "+ str(droneID) + " Has Reached Altitude...")

    def arm_and_takeoff(self,aTargetAltitude):
        self.arm()  

        self.vehicle.add_attribute_listener('location.global_relative_frame', self.location_callback)
        self.vehicle.add_attribute_listener('armed', self.armed_callback)
        self.vehicle.add_attribute_listener('mode', self.mode_callback)
        
        self.logger.info ("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        while True:
            self.logger.info ("Vehicle Altitude: " + str(self.vehicle.location.global_relative_frame.alt))
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude*.95: 
                self.logger.info ("Reached target altitude")
                #self.send_data_to_server("/dronedata", self.get_drone_data())
                break
            time.sleep(.75) 
         
    def arm_formation(self):
        master_params = self.get_data_from_server("/dronedata",{'droneID':'1'})
        self.logger.info ("MASTER_PARAMS CAME BACK AS: " + str(master_params))
        
        while master_params == "NO_DRONE_DATA":
            self.logger.info ("No Master Drone Found Registered On Swarm")
            time.sleep(1)
            master_params = self.get_data_from_server("/dronedata",{'droneID':'1'})
            
        if master_params["armed"] == True:
            self.logger.info ("Drone : " + master_params["id"] + " armed status - " + master_params["armed"])
            self.arm()
        else:
            self.logger.info ("Drone : " + master_params["id"] +  " armed status - " + master_params["armed"])
        
        self.arm_no_GPS()

    def goto(self):
        pass

    def land_vehicle(self):
        self.logger.info("Returning to Launch!!!")

        if not self.sitlRunning:
            self.vehicle.parameters["RTL_ALT"] = 0.0
            self.vehicle.airspeed = 1
        else:
            self.vehicle.airspeed = 3
            
        self.vehicle.mode = VehicleMode("RTL")
        while self.vehicle.mode.name != "RTL":
            self.logger.info("Vehicle Mode Didn't Change")
            self.vehicle.mode = VehicleMode("RTL")
            time.sleep(1)
        #http://ardupilot.org/copter/docs/parameters.html#rtl-alt-rtl-altitude
        while self.vehicle.location.global_relative_frame.alt > 0.2 :
            self.logger.info("Altitude: " + str(self.vehicle.location.global_relative_frame.alt))
            time.sleep(1)
        self.logger.info("Landed!")

