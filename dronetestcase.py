from droneBrain2 import Drone
from droneData2 import Swarm
from server2 import Server
from dronekit_sitl import SITL
import dronekit
import unittest
from config import load_json_config

class testConfig():
    def __init__(self):
        self.drones = []
        self.sitlInstance = []
        self.swarmSize = 0

        c = load_json_config('swarm_config').Drones

        for idx, drone_cfg in enumerate(c):
            sitl = SITL('/home/dino/.dronekit/sitl/copter-3.3/apm')
            sitl_args = ['--instance ' + str(idx), '-I0', '--model', 'quad', '--home=-35.363261,149.165230,584,353']
            sitl.launch(sitl_args, verbose=False, await_ready=False, restart=True)
            self.sitlInstance.append(sitl)
            self.drones.append(Drone(drone_cfg))
            self.swarmSize = self.swarmSize + 1


class dronetestcase(unittest.TestCase):
    def setUpClass(self):
        #cfg = testConfig()

    def setUp(self):
        self.swarm_cfg = load_json_config('swarm_config')
        self.swarm = Swarm(self.swarm_cfg)

    def test_swarm_size(self):
        self.assertEqual(self.swarm.swarm_size(), self.swarm_cfg.Drones.__len__())

    def test_wait_for_swarm_ready(self):
        self.swarm.wait_for_swarm_ready()
    ""
    """def test_sitl_instance(self):
        sitl = cfg.sitlInstance[cfg.swarmSize-1]
        self.assertIsInstance(sitl, SITL)
    """
    """def test_swarm(self):
        self.swarm = Swarm()
        self.assertTrue(self.swarm)

    def test_drone(self):
        drone = self.drones[self.swarmSize-1]
        drone.arm_and_takeoff(10)
        new_data = drone.get_drone_data()
        drone_ip = new_data.ip
        drone_id = new_data.id
        drone_airspeed = new_data.airspeed
        drone_latitude = new_data.latitude
        drone_longitude = new_data.longitude
        drone_altitude = new_data.altitude
        drone_armed = new_data.armed
        drone_mode = new_data.mode

        #Begin testing JSON Object
        self.assertEqual((drone_id,drone_ip),(drone.id,drone.ip))
        self.assertIs(drone_airspeed, None)
        self.assertIs(drone_latitude, None)
        self.assertIs(drone_longitude, None)
        self.assertEqual(drone_altitude, None)
        self.assertIs(drone_armed, False)
        self.assertIs(drone_mode, "STABILIZE")
        drone.land_vehicle()


    """
    """def test_add_to_swarm(self):
        self.swarm = Swarm()
        for idx, drone in enumerate(self.drones):
            self.swarm.addDrone(self.drones[idx])
            self.assertTrue(self.swarm.swarmSize(), idx+1)
    """
    """def test_webserver(self):
        self.swarm = Swarm()
        self.server = Server(self.swarm)
        self.assertTrue(self.server)
    """

if __name__ == '__main__':
    unittest.main()
