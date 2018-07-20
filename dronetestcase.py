import requests

from droneBrain2 import Drone
from droneData2 import Swarm
import unittest
from config import load_json_config

class DroneUnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.swarm_config = load_json_config("swarm_config")

        self.swarm = Swarm(self.swarm_config.Swarm)
        self.ip = self.swarm.ip
        self.webport = self.swarm.webport
        self.swarmSize = 0

        self.swarm_data_structure = {
            "Swarm": {
                "size": self.swarmSize,
                "ip": self.ip,
                "webport": self.webport
            },
            "Drones": []
        }

        #idx is zero based so we make is not
        self.swarmSize += 1
        ######################################

        print("Setup testConfig() complete!")

class FirstSetOfTests(DroneUnitTest):
    @classmethod
    def setUpClass(self):
        super(FirstSetOfTests, self).setUpClass()

    def test_add_to_swarm(self):

        expectedDroneCount = 0
        for idx, drone in enumerate(self.swarm_config.Drones):
            drone = Drone(self.swarm_config.Drones[idx])
            self.swarm_data_structure.get("Drones").append(drone)
            drone.update_self_to_swarm('/Swarm')
            expectedDroneCount += 1

        drone = self.swarm_data_structure.get("Drones")[0]
        swarmData = drone.get_data_from_server("/Swarm")
        actualDroneCount = len(swarmData.Drones)

        self.assertEqual(actualDroneCount, expectedDroneCount)


    def test_wait_for_swarm_ready(self):
        self.swarm.wait_for_swarm_ready(len(self.swarm_data_structure.get("Drones")))

    def test_swarm(self):
        swarm_config = load_json_config("swarm_config")
        self.swarm = Swarm(swarm_config.Swarm)
        self.assertTrue(self.swarm)


    #for the swarm movement test cases I will have to spawn a thread for each drone
    def test_swarm_takeoff_altitude(self):
        altitude = 10
        for idx, drone in enumerate(self.swarm_data_structure.get("Drones")):
            drone.arm_and_takeoff(10)
        self.swarm_data_structure.get("Drones")[0].wait_for_swarm_to_match_altitude()


    ""
    """def test_sitl_instance(self):
        sitl = cfg.sitlInstance[cfg.swarmSize-1]
        self.assertIsInstance(sitl, SITL)
    
    """

if __name__ == '__main__':
    unittest.main()
