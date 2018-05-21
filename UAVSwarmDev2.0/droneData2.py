#=============================droneData.py===================================================================
# Author: Martin Pozniak, Joey Schwalb
# Desc: This class is used by server.py to control and keep track of the swarm data.
# Creation Date: 12/~/2017
#=============================================================================================================

#--------------What the Drone data structure will look like--------------
#-------This is not the actual object used to store active drones--------
# ----a one element list, which contains a dictionary--------------------
#-----whose keys are the Drone ID, and whose value is another dict containing the params------
from droneBrain2 import Drone
Drones = [
            {
            "id":'1',
            "ip":"192.168.x.x",
            "latitude":"~",
            "longitude":"~",
            "altitude":"~",
            "armed":"False",
            "mode":"vehicle.mode"
            },
            {
            "id":'2',
            "ip":"192.168.x.x",
            "latitude":'~',
            "longitude":'~',
            "altitude":'~',
            "armed":"False",
            "mode":"vehicle.mode"
            }
        ]
#--------------------^^For Visual Aid Only^^----------------------------

#=============================SWARM CLASS | CONTAINS SWARM OPERATIONS===================================
#=======================================================================================================
class Swarm(object) :

    #=============================SWARM CONSTRUCTOR=========================================================
    #=======================================================================================================
    def __init__(self):
        self.swarm = []

    #=============================MEMBER FUNCTIONS==========================================================
    #=======================================================================================================
    def addDrone(self,drone):
        #This function is used to add a drone to the swarm.
        self.swarm.append(drone.id)
        print("\nAdded a drone with params",drone,"\n")
        print("Current Swarm Stats\n----------------------\n",self.swarm,"\n")

    def removeDrone(self,data):
        indxDroneToRemove = self.getIndexOfDroneByID(data["id"])
        self.swarm.remove(indxDroneToRemove)
        print("\nRemoved a drone with params",data,"\n")
        print("Current Swarm Stats\n----------------------\n",self.swarm,"\n")

    def findDroneByID(self,droneID):
        for drone in self.swarm:
            if(drone["id"]==droneID):
                return drone
        return "No Drone found with ID of " + (str)(droneID)

    def droneExists(self,droneID):
        for drone in self.swarm:
            if drone["id"]==droneID:
                return True
        return False

    def getIndexOfDroneByID(self,droneID):
        for i, drone in enumerate(self.swarm,1):
            if(drone["id"]==droneID):
                return i
        return "No Drone found with ID of " + (str)(droneID)

    def getNumNodesInSwarm(self):
        return self.swarm.len()

    def updateDroneInfo(self, newData):
        #print("Data received in update: ",data," TYPE: ",type(data))
        #print("UPDATING DRONE #",data["id"])
        indxDroneToUpdate = self.getIndexOfDroneByID(newData["id"])
        if self.swarm[indxDroneToUpdate] != None:
            self.swarm[indxDroneToUpdate] = newData
            print("\nSuccessfully Updated Drone: ",self.swarm[indxDroneToUpdate])
            #print("Current Swarm Stats\n----------------------\n", self.getSwarmData(),"\n")
            return self.swarm[indxDroneToUpdate]
        else:
            print("\nDid not find drone by id, no record updated\n")
            return  "NO_DATA"

    def getSwarmData(self):
        return self.swarm

    def getDroneInfo(self,idOfDrone):
        #print("\n\n DRONE PARAMS TO RETURN: ",self.findDroneByID(idOfDrone),"\n\n")
        return self.findDroneByID(idOfDrone)

    def listSwarm(self):
        for i in (0,self.swarm.len()):
            print("Drone #" + (str)(i) + ": " + (str)(self.swarm[i]))
