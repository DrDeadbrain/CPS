from scipy.spatial import distance

'''
Class that represents a road
-> in order to draw a road on the window we need its length and the sine 
and cosine of its angle
'''


class Road:
    def __init__(self, start, end):
        self.angle_cos = None
        self.angle_sin = None
        self.length = None
        self.start = start
        self.end = end

        self.init_properties()

    def init_properties(self):
        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1] - self.start[1]) / self.length
        self.angle_cos = (self.end[0] - self.start[0]) / self.length
