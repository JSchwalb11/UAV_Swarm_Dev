from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

"""
DRONES = {
    [
        "12": {
            "id": "12",
            "ip": "192.168.1.2",
            "airspeed": "3",
            "latitude": "97.37574",
            "longitude": "68.38475",
            "altitude": "4.7",
            "armable": "1",
            "armed": "0",
            "mode": "GUIDED"
        },
        "15": {
            "id": "15",
            "ip": "192.168.1.2",
            "airspeed": "3",
            "latitude": "97.37574",
            "longitude": "68.38475",
            "altitude": "4.7",
            "armable": "1",
            "armed": "0",
            "mode": "GUIDED"
        }
        
    ]
}
"""
Swarm = {
    "Drones": [{
        "12": {
            "id": "12",
            "ip": "192.168.1.2",
            "airspeed": "3",
            "latitude": "97.37574",
            "longitude": "68.38475",
            "altitude": "4.7",
            "armable": "1",
            "armed": "0",
            "mode": "GUIDED"
        },
        "15": {
            "id": "15",
            "ip": "192.168.1.2",
            "airspeed": "3",
            "latitude": "97.37574",
            "longitude": "68.38475",
            "altitude": "4.7",
            "armable": "1",
            "armed": "0",
            "mode": "GUIDED"
        }}],
    "Swarm": {
        "size": 1,
        "ip": '127.0.0.1',
        "webport": '5000'
    }
}


def abort_if_todo_doesnt_exist(drone_id):
    for idx, drone in enumerate(Swarm.get("Drones")):
        if drone.id == drone_id:
            return idx
    abort(404, message="Drone {} doesn't exist".format(drone_id))

parser = reqparse.RequestParser()
parser.add_argument('drone')
parser.add_argument('swarm')


# Drone
# shows a single drone and allows for adding and deleting
class Drone(Resource):

    def get(self, drone_id):
        index_of_drone = abort_if_todo_doesnt_exist(drone_id)
        return Swarm.get("Drones")[index_of_drone]

    def delete(self, todo_id):
        index_of_drone = abort_if_todo_doesnt_exist(todo_id)
        del Swarm.get("Drones")[index_of_drone]
        return '', 204

    def put(self, drone_id):
        args = parser.parse_args()
        drone_config = {args.id: args['drone']}
        swarm_config = {'swarm': args['swarm']}
        Swarm.get('Drones').update(drone_config)
        Swarm.get('Swarm').update(swarm_config)
        return 201


# DroneList
# shows a list of all Drones, and lets you POST to add new drones
class DroneList(Resource):
    def get(self):
        return Swarm

    def post(self):
        args = parser.parse_args()
        print("Drone ID before posting (As it is in the json object):" + str(args.id))
        drone_id = int(max(Swarm.get('Drones').keys()).lstrip('drone')) + 1
        print("Drone ID after stripping drones:" + str(drone_id))

        drone_id = 'todo%i' % drone_id
        Swarm.get("Drones")[drone_id].append({'task': args['task']})
        return 201


	   
api.add_resource(DroneList, '/Swarm')
api.add_resource(Drone, '/Swarm/<drone_id>')


if __name__ == '__main__':
    app.run(debug=True)