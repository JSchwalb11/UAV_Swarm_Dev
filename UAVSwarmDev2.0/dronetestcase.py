from droneBrain2 import Drone
from droneData2 import Swarm
from server2 import Server
import dronekit_sitl
import dronekit
import unittest
from config import load_json_config

class dronetestcase(unittest.TestCase):
    def setUp(self):
        self.drones = []
        for drone_cfg in load_json_config('swarm_config').Drones:
            self.drones.append(Drone(drone_cfg))

    def test_swarm(self):
        self.swarm = Swarm()
        self.assertTrue(self.swarm)

    def test_add_to_swarm(self):
        self.swarm = Swarm()
        for idx, drone in enumerate(self.drones):
            self.swarm.addDrone(self.drones[idx])
            self.assertTrue(self.swarm.swarmSize(), idx+1)

    """def test_webserver(self):
        self.swarm = Swarm()
        self.server = Server(self.swarm)
        self.assertTrue(self.server)
    """

if __name__ == '__main__':
    unittest.main()
