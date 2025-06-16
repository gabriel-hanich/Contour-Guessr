class Coord:
    # Stores a lat/long coordinate
    def __init__(self, latitude, longitude):
        self.lat = latitude
        self.long = longitude
    
    def __str__(self):
        return f"({self.lat}N, {self.long}W)"
    
class BoundingBox:
    # Defines a bounding box using two coordinates
    # One Coord is the South-West corner of the box and the other is the North-East corner
    def __init__(self, c1, c2):
        if (c1.long <= c2.long) and (c1.lat <= c2.lat): 
            self.SW = c1
            self.NE = c2
        else:
            self.SW = c2
            self.NE = c1

    def __str__(self):
        return f"South West Corner: {self.SW}    North East Corner: {self.NE}"
    
    def getBound(self, descriptor):
        # Get the bounding lat/long depending on the edge specified
        if descriptor.lower() in ["top", "north"]:
            return self.NE.lat
        if descriptor.lower() in ["bottom", "south"]:
            return self.SW.lat
        if descriptor.lower() in ["right", "east"]:
            return self.NE.long
        if descriptor.lower() in ["left", "south"]:
            return self.SW.long

    def contains(self, coord):
        # Returns whether or not a coordinate is within the bounding box
        isLat = (coord.lat >= self.SW.lat) and (coord.lat <= self.NE.lat)
        isLong = (coord.long >= self.SW.long) and (coord.long <= self.NE.long)
        return isLat and isLong 
    

class MapImage:
    def __init__(self, id, mapBounds, pixelBoundingBox, pixelsPerMeter):
        self.id = id
        self.mapBounds = mapBounds
        self.pixelBoundingBox = pixelBoundingBox
        self.pixelsPerMeter = pixelsPerMeter
    
        self.pixelsPerLat = abs(pixelBoundingBox["top"] - pixelBoundingBox["bottom"]) / abs(self.mapBounds.NE.lat - self.mapBounds.SW.lat)
        self.pixelsPerLong = abs(pixelBoundingBox["left"] - pixelBoundingBox["right"]) / abs(self.mapBounds.NE.long - self.mapBounds.SW.long)

    
    def getPixelCoords(self, coord):
        # Takes a lat/long coordinate and returns the (x,y) coordinates of the corresponding pixel
        if not self.mapBounds.contains(coord):
            raise Exception(f"The provided coordinates are not within the bounding box of map {self.id}")

        minDistance = -1
        nearestCornerPixel = [] 
        nearestCornerDeg = []
        multipliers = []
        multi = [1, -1]
        for xIndex, x in enumerate(["left", "right"]):
            for yIndex, y in enumerate(["top", "bottom"]):
                c = Coord(self.mapBounds.getBound(y),self.mapBounds.getBound(x))
                dist = calculateDistance(c, coord) 
                if (minDistance == -1) or dist < minDistance:
                    minDistance = dist
                    nearestCornerPixel = (self.pixelBoundingBox[x], self.pixelBoundingBox[y])
                    nearestCornerDeg = c    
                    multipliers = [multi[xIndex], multi[yIndex]]
        xCoord = multipliers[0] * (abs(coord.long - nearestCornerDeg.long) * self.pixelsPerLong) + nearestCornerPixel[0]
        yCoord = multipliers[1] * (abs(coord.lat - nearestCornerDeg.lat) * self.pixelsPerLat) + nearestCornerPixel[1]
        return [xCoord, yCoord]


def calculateDistance(c1, c2):
    try:
        return ((c1.lat - c2.lat) ** 2 + (c1.long - c2.long) ** 2) ** 0.5
    except AttributeError:
        return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5
    

def getValidStreetViewPos(streetViewData, mapBoundingBox, userBoundingBox, oldestYr):
    inBoundCoords = []

    for point in streetViewData["customCoordinates"]:
        coord = Coord(point["lat"], point["lng"])
        yr = max(int(val.split("-")[0]) for val in point["extra"]["tags"])
        if mapBoundingBox.contains(coord) and userBoundingBox.contains(coord):
            if yr >= oldestYr:
                inBoundCoords.append(coord)
    
    return inBoundCoords
        

def mergeBoundingBoxes(boxes):
    # Takes a list of bounding boxes and converts them to one
    # bounding box that covers the whole area
    top = 200
    left = 200
    bottom = 200
    right = 200
    for bBox in boxes:
        if (bBox.getBound("top") > top) or (top == 200):
            top = bBox.getBound("top")
        if (bBox.getBound("left") < left) or (left == 200):
            left = bBox.getBound("left")
        if (bBox.getBound("bottom") < bottom) or (bottom == 200):
            bottom = bBox.getBound("bottom")
        if (bBox.getBound("right") > right) or (right == 200):
            right = bBox.getBound("right")

    return BoundingBox(Coord(bottom, left), Coord(top, right))

def getMap(loc, maps):
    # Returns the map a given location is within
    for mapImg in maps:
        if mapImg.mapBounds.contains(loc):
            return mapImg
    raise Exception("Could not find a map containing the given coordinates")