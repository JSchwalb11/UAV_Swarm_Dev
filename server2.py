#=============================server.py===================================================================
# Author: Martin Pozniak
# Desc: This script controls the server routing and handling of HTTP requests from the drones...
# Creation Date: 12/~/2017
#=============================================================================================================
from flask import Flask
from droneData2 import Swarm
import site
from flask_restful import Resource, Api, abort, reqparse
print(site.USER_SITE)
import gevent.pywsgi



class Server():

    def __init__(self, swarm):
        self.swarm = swarm

        app = Flask(__name__)
        self.api = Api(app)

        self.api.add_resource(Swarm.get_swarm(self.swarm), '/Swarm')
        for idx, drone in enumerate(self.swarm):
            self.newDrone(drone)

        if __name__ == "__main__":
            self.gevent_server = gevent.pywsgi.WSGIServer(('', 5000), self.app)
            self.gevent_server.serve_forever() #instead of self.app.run()


    def newDrone(self, drone):
        self.api.add_resource(Swarm.get_drone(self.swarm, drone.id))
        self.api.add_resource(drone.get_drone_data(), '/Swarm/' + str(drone.id))



#=============================CREATE A SWARM INSTANCE===================================================
#=======================================================================================================



#=============================HANDLE REQUESTS FOR ADDING DRONE TO SWARM=================================
"""
@app.route('/')
def index():
    return render_template('webpage.html')

@app.route('/adddrone', methods=['POST'])
def clientIsAddingDrone():
    if request.method == 'POST':
        print("\n=================ADDING_DRONE=============================")
        swarm.addDrone(request.get_json(force=True))
        print("==============================================================\n")
        return swarm.getDroneInfo(request.get_json(force=True)["id"])
    print("==============================================================\n")
    return "NO_DATA"

#=============================HANDLE REQUESTS FOR REMOVING DRONE FROM SWARM=================================
#===========================================================================================================
@app.route('/removedrone', methods=['POST'])
def clientIsRemovingDrone():
    if request.method == 'POST':
        print("\n=================REMOVING_DRONE=============================")
        swarm.removeDrone(request.get_json(force=True))
        print("======================PASS=================================\n")
        return swarm.getSwarmData()
    print("======================NO_DATA=================================\n")
    return "NO_DATA"

#=============================HANDLE REQUESTS FOR DRONE DATA============================================
#=======================================================================================================
@app.route('/dronedata', methods=['GET', 'POST'])
def clientRequestedDroneData():
    if request.method == 'POST':
        print("\n=================POST_DRONE_DATA=============================")
        print("Data To Post: ", request.data)
        try:
            drone = swarm.updateDroneInfo(request.get_json(force=True))
            if drone != "NO_DATA":
                print("======================PASS====================================")
                return drone
        except:
            print("\nError Occured While Attempting To Update Drone Data\nError is likely due to drone no longer in swarm, or error occured in droneData.py > updateDroneData()")
            print("=====================NO_DATA=================================")
            return "NO_DRONE_DATA"


    if request.method == 'GET':
        print("\n=================GET_DRONE_DATA=============================")
        print("\nGETTING DATA FOR DRONE : ",request.data['droneID'], type(request.data['droneID']))
        droneToReturn = swarm.getDroneInfo(request.data['droneID'])
        if droneToReturn is not None :
            print("==================PASS===================================")
            return swarm.getDroneInfo(request.data['droneID'])

    print("==========================NO_DATA============================")
    return "NO_DRONE_DATA"

def processDroneData():
    if request.method == 'GET':
        print("\n=================GET_DRONE_DATA=============================")
        print("\nGETTING DATA FOR DRONE : ", request.data['droneID'], type(request.data['droneID']))
        droneToReturn = swarm.getDroneInfo(request.data['droneID'])
        if droneToReturn is not None:
            print("Successful Drone data return!")
            return swarm.getDroneInfo(request.data['droneID'])
    elif request.method == 'POST':
        print("\n=================POST_DRONE_DATA=============================")
        print("Data To Post: ", request.data)
        drone = swarm.updateDroneInfo(request.get_json(force=True))
        if drone != "NO_DATA":
            print("======================PASS====================================")
            return drone
        print("\nError Occured While Attempting To Update Drone Data\nError is likely due to drone no longer in swarm, or error occured in droneData.py > updateDroneData()")
        print("=====================NO_DATA=================================")
        return "NO_DATA"

#=============================HANDLE REQUESTS FOR SWARM DATA============================================
#=======================================================================================================
@app.route('/swarmdata', methods=['GET'])
def clientRequestedSwarmData():
    if request.method == 'GET':
        print("\n=================GET_SWARM_DATA=============================")
        swarmToReturn = swarm.getSwarmData()
        print("RETURNING: ",swarmToReturn)
        print("=======================PASS===============================")
        if swarmToReturn is not None :
            return swarmToReturn
    print("=======================NO_SWARM_DATA===============================")
    return "NO_SWARM_DATA"

#=============================PROVIDE A GUI FOR THE SYSTEM============================================================
#=====================================================================================================================
@app.route('/', methods=['GET'])
def clientRequestedGui():
    return render_template("index.html")

#=============================RUN THE SERVER============================================================
#=======================================================================================================

"""