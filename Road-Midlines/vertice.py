from shapely.geometry.point import Point
from shapely.geometry import GeometryCollection

class Vertice:
    def __init__(self, all_grids, xmin, ymin, xmax, ymax, grid_size, x, y):
        self.x = x
        self.y = y
        self.point = Point(x, y)
        self.row = int((x-xmin) // grid_size)
        self.col = int((y-ymin) // grid_size)
        if (x < xmin) or (y < ymin) or (x > xmax) or (y > ymax):
            self.withinBuffer = False
        elif (all_grids[self.row, self.col].bufferUnionTrimmed is None) or \
                (type(all_grids[self.row, self.col].bufferUnionTrimmed) == GeometryCollection):
            self.withinBuffer = False
        else:
            self.withinBuffer = self.point.within(all_grids[self.row, self.col].bufferUnionTrimmed)
