from road import Road


class Simulation:
    def __init__(self, config={}):
        # set default config
        self.set_default_config()

        # update config
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.t = 0.0  # Time
        self.frame_count = 0  # Frame Count
        self.dt = 1 / 60  # Simulation time step
        self.roads = []  # array to store roads

    def create_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)
