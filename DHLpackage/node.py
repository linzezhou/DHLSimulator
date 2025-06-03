import simpy
class Node:
    def __init__(self, env, name, config):
        self.env = env
        self.name = name
        self.docking_stations = simpy.Resource(env, capacity=config['docking_stations'])
        self.current_ssd = None 