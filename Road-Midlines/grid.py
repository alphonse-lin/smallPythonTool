from numpy import sqrt
from shapely.ops import unary_union
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry.multipolygon import MultiPolygon


area_threshold = 100   # Threshold for holes whose areas smaller than it should be removed
width_threshold = 10


def gridList2Polygon(gridList):
    bottomLeft = [gridList[0], gridList[1]]
    bottomRight = [gridList[2], gridList[1]]
    topLeft = [gridList[0], gridList[3]]
    topRight = [gridList[2], gridList[3]]
    gridRing = LinearRing([bottomLeft, bottomRight, topRight, topLeft, bottomLeft])
    grid = Polygon(gridRing)
    return grid


def remove_polygon_holes(myPolygon):
    def calculate_linering_area(myLinering):
        myRing = Polygon(myLinering)
        myArea = myRing.area
        return myArea

    def calculate_polygon_width(myPolygon):
        myPolygon_utm_rect = myPolygon.minimum_rotated_rectangle
        s = myPolygon_utm_rect.area
        l = myPolygon_utm_rect.length / 2
        # a = l / 2 + sqrt(l * l / 4 - s)
        b = l / 2 - sqrt(l * l / 4 - s)
        return b

    inner_rings = [x for x in myPolygon.interiors]
    inner_rings = [x for x in inner_rings if (calculate_linering_area(x) > area_threshold) and (calculate_polygon_width(x) > width_threshold)]
    outer_ring = myPolygon.exterior
    new_buffer = Polygon(outer_ring, inner_rings)
    return new_buffer


class Grid():
    def __init__(self, xmin=None, ymin=None, xmax=None, ymax=None):
        self.bottomLeft = [xmin, ymin]
        self.topRight = [xmax, ymax]
        self.gridPolygon = gridList2Polygon([xmin, ymin, xmax, ymax])
        self.road = None
        self.buffer = None
        self.bufferUnion = None
        self.bufferUnionTrimmed = None


    def setRoadAndBuffer(self, myRoad, dist):
        self.road = myRoad
        if len(myRoad)>0:
            df_buffer = [x.buffer(distance=dist) for x in myRoad]
            df_buffer = unary_union(df_buffer)
            self.buffer = df_buffer


    def setBufferUnion(self, bufferList):
        allBuffer = bufferList + [self.buffer]
        allBuffer = [x for x in allBuffer if x is not None]
        allBuffer = [x if x.is_valid else x.buffer(0) for x in allBuffer]
        if len(allBuffer)>0:
            self.bufferUnion = unary_union(allBuffer)
            if type(self.bufferUnion) == MultiPolygon:
                self.bufferUnion = MultiPolygon([remove_polygon_holes(x) for x in self.bufferUnion])
            elif type(self.bufferUnion) == Polygon:
                self.bufferUnion = remove_polygon_holes(self.bufferUnion)
            self.bufferUnionTrimmed = self.bufferUnion.intersection(self.gridPolygon)
            if self.bufferUnionTrimmed.is_empty:
                self.bufferUnionTrimmed = None
