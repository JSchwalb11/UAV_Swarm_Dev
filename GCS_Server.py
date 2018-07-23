from flask import Flask, render_template, request, make_response
from flask_restful import reqparse, abort, Api, Resource
from config import Config

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
    "Drones": [],
    "Swarm": {
        "size": 1,
        "ip": '127.0.0.1',
        "webport": '5000'
    }
}

def update_dict(dictionary):
    dictionary = Config(dictionary)
    return dictionary


def abort_if_todo_doesnt_exist(drone_id):
    for idx, drone in enumerate(Swarm.get("Drones")):
        if drone.get("id") == drone_id:
            return idx
    abort(404, message="Drone {} doesn't exist".format(drone_id))

def exists(droneid):
    for idx, drone in enumerate(Swarm.get("Drones")):
        if Swarm.get("Drones")[idx].get("id") == droneid:
            return True
    return False

def index_of(id):
    for idx, drone in enumerate(Swarm.get("Drones")):
       if drone.get("id") == id:
           return idx



parser = reqparse.RequestParser()
parser.add_argument("id")
parser.add_argument('ip')
parser.add_argument('airspeed')
parser.add_argument('latitude')
parser.add_argument('longitude')
parser.add_argument('altitude')
parser.add_argument('armable')
parser.add_argument('armed')
parser.add_argument('mode')


# Drone
# shows a single drone and allows for adding and deleting
class Drone(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("id")
    parser.add_argument('ip')
    parser.add_argument('airspeed')
    parser.add_argument('latitude')
    parser.add_argument('longitude')
    parser.add_argument('altitude')
    parser.add_argument('armable')
    parser.add_argument('armed')
    parser.add_argument('mode')

    def get(self):
        object_args = parser.parse_args()
        object_id = object_args.get("id")
        index_of_drone = abort_if_todo_doesnt_exist(object_id)
        return Swarm.get("Drones")[index_of_drone]

    def delete(self, todo_id):
        object_args = parser.parse_args()
        object_id = object_args.get("id")
        index_of_drone = abort_if_todo_doesnt_exist(todo_id)
        del Swarm.get("Drones")[index_of_drone]
        return '', 204

    def put(self):
        #object_args = parser.parse_args()
        #object_id = object_args.get("id")
        #object_config = {object_args.get("obj")}
        #drone_config = object_config.__dict__[object_id]


        #dict(id=args.get("id"), ip=args.get("ip"), airspeed=args.get("airspeed"), latitude=args.get("latitude"),
        #     longitude=args.get("longitude"), altitude=args.get("altitude"), armable=args.get("armable"),
        #     armed=args.get("armed"), mode=args.get("mode"))
        #            }

        #drone_config = {args.id: args['drone']}
        #swarm_config = {'swarm': args['swarm']}
        #Swarm.get('Swarm').update(swarm_config)
        #Swarm.get('Drones').append(drone_config)
        return 201


# DroneList
# shows a list of all Drones, and lets you POST to add new drones
class DroneList(Resource):
    def get(self):
        return Swarm

    def post(self):
        args = parser.parse_args()
        object_config = {
            "id": args.get("id"),
            "ip": args.get("ip"),
            "airspeed": args.get("airspeed"),
            "latitude": args.get("latitude"),
            "longitude": args.get("longitude"),
            "altitude": args.get("altitude"),
            "armable": args.get("armable"),
            "armed": args.get("armed"),
            "mode": args.get("mode")
             }

        #Swarm.get('Swarm').update(swarm_config)
        Swarm.get('Drones').update(object_config)
        return

    def put(self):
        args = parser.parse_args()
        #fix this dictionary
        object_config = {
                            "id": args.get("id"),
                            "ip": args.get("ip"),
                            "airspeed": args.get("airspeed"),
                            "latitude": args.get("latitude"),
                            "longitude": args.get("longitude"),
                            "altitude": args.get("altitude"),
                            "armable": args.get("armable"),
                            "armed": args.get("armed"),
                            "mode": args.get("mode")
                        }

        #Swarm.get('Swarm').update(swarm_config)
        ID_to_check = object_config.get("id")
        if exists(ID_to_check):
            idx = index_of(ID_to_check)
            Swarm.get("Drones")[idx] = object_config
        else:
            Swarm.get('Drones').append(object_config)
        """
        [x for x in c.Drones if x.id == '15']
        
        list = []
        for x in c.Drones:
            if x.id == '15'
                list.append(x)
        return list
        
        Option1:
            Head of the list == swarm leader c.Drones[0]
        Option2:
            [x for x in c.Drones if x.head]
        Option3:
            Use the Id's as keys c.Drones["someidhere"]
            [x for x in c.Drones.values if x.id == '15']

        """
@app.route('/test1/')
def test1():
    return render_template('test1.html')

@app.route('/map/')
def map():
    s = render_template('map.html')
    response = make_response(s)
    response.headers['Access-Control-Allow-Origin'] = '127.0.0.1'
    return response

	   
api.add_resource(DroneList, '/Swarm')
#api.add_resource(Drone, '/Swarm/<drone_id>')


if __name__ == '__main__':
    app.run(debug=True, port= 5550)