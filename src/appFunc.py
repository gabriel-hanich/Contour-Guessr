import cliFunc as cli
import os
import time
import json
from geoManager import Coord, BoundingBox, MapImage, mergeBoundingBoxes, getValidStreetViewPos, calculateDistance
import matplotlib.pyplot as plt

clickLocs = []

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def establishSetup(roundSetup):
    # Asks the user for their preferences to set up the round
    # Fill in the blanks for the variable parameters
    if roundSetup["rounds"] == "?":
        roundSetup["rounds"] = cli.getIntegerInput("How many rounds do you want to play?", minVal=0, maxVal=99)

    # Get a list of maps
    mapList = list(folder.name for folder in os.scandir("./data/maps"))
    if len(mapList) == 0:
        print(f"{colors.FAIL}ERROR - No Maps downloaded{colors.ENDC}")
        print(f"{colors.FAIL}There are no maps available in 'data/maps'{colors.ENDC}")
        exit()

    if roundSetup["map"] == "?" or (not roundSetup["map"] in mapList):
        roundSetup["map"] = cli.selectListElem("Which map do you want to play?", mapList)

    # Get a list of map versions
    mapVersionList = list(folder.name for folder in os.scandir(f"./data/maps/{roundSetup['map']}"))
    if len(mapVersionList) == 0:
        print(f"{colors.FAIL}ERROR - No Map Versions{colors.ENDC}")
        print(f"{colors.FAIL}'{roundSetup['map']}' has no versions, they may have been deleted{colors.ENDC}")
        exit()

    if roundSetup["map-version"] == "?" or (not roundSetup["map-version"] in mapVersionList):
        roundSetup["map-version"] = cli.selectListElem("Which version of the map do you want to play?", mapVersionList)


    if roundSetup["seed"] == "?":
        roundSetup["seed"] = input("What random seed do you want to use?")
    elif roundSetup["seed"] == "":
        roundSetup["seed"] = round(time.time())

    if roundSetup["score-algorithm"] == "?":
        roundSetup["score-algorithm"] = cli.selectListElem("Which scoring algorithm do you want to use?", ["linear"])
    
    roundSetup["bounding-box"] = BoundingBox(
        Coord(roundSetup["bounding-box"]["south"], roundSetup["bounding-box"]["west"]),
        Coord(roundSetup["bounding-box"]["north"], roundSetup["bounding-box"]["east"])
        )

    return roundSetup

def showAppSetup(roundSetup, streetViewLocs, mapMeta):
    # Prints the round's setup
    print(f"\nGame Setup")
    bar = "-" * 60
    print(f"{bar}\n{'Map':<30} | {roundSetup['map']}")
    print(f"{'Map Version':<30} | {roundSetup['map-version']}")
    print(f"{'Number of Rounds':<30} | {roundSetup['rounds']}")
    print(f"{'Map Scale':<30} | 1:{mapMeta['scale']}")
    print(f"{'No# of Maps':<30} | {mapMeta['mapCount']}")
    print(f"{colors.OKBLUE}{'No# of Possible Locations':<30} | {len(streetViewLocs)}{colors.ENDC}\n{bar}")


def loadData(roundSetup):
    # Loads the streetview locations, map metadata 
    # and ensures the required number of maps exist 

    # Streetview data
    try:
        filePath = "./data/streetview/australia.json"
        with open(filePath, "r") as streetViewFile:
            streetViewData = json.load(streetViewFile)
    except FileNotFoundError:
        print(f"{colors.FAIL}ERROR - Could not find the streetview file\nUnable to find the streetview file located at '{filePath}'{colors.ENDC}")
        exit()

    # Load the map data
    try:
        filePath = f"./data/maps/{roundSetup['map']}/{roundSetup['map-version']}/mapData.json"
        with open(filePath, "r") as mapMetaFile:
            mapMeta = json.load(mapMetaFile)
    except FileNotFoundError:
        print(f"{colors.FAIL}ERROR - Could not find the mapData file\nUnable to find the mapData file located at '{filePath}'{colors.ENDC}")
        exit()

    # Load the map grid data
    try:
        filePath = f"./data/maps/{roundSetup['map']}/{roundSetup['map-version']}/mapGrid.csv"
        with open(filePath, "r") as mapGridFile:
            lines = mapGridFile.readlines()
            mapGrid = list(val.split(",") for val in lines[1:])
    except FileNotFoundError:
        print(f"{colors.FAIL}ERROR - Could not find the mapGrid file\nUnable to find the mapGrid file located at '{filePath}'{colors.ENDC}")
        exit()
    
    # Ensure the required number of maps are present 
    filePath = f"./data/maps/{roundSetup['map']}/{roundSetup['map-version']}"
    folderFiles = list(mapFile.name for mapFile in os.scandir(filePath))
    mapFiles = list(filter((lambda x: ".png" in x), folderFiles))
    if len(mapFiles) != mapMeta["mapCount"]:
        print(f"{colors.FAIL}ERROR - Missing Maps\nMap meta data says there should be {mapMeta['mapCount']}, but only {len(mapFiles)} could be found in {filePath} {colors.ENDC}")

    # Convert the data into the relavent formats
    
    mapImgs = []
    for line in mapGrid: 
        coords = BoundingBox(Coord(float(line[5]), float(line[2])), Coord(float(line[3]), float(line[4])))
        mapImgs.append(MapImage(line[1], coords, mapMeta["pixel-boundingBox"], mapMeta["pixelsPerMeter"]))

    mapBounding = mergeBoundingBoxes(list(mp.mapBounds for mp in mapImgs))

    streetViewPoints = getValidStreetViewPos(streetViewData, mapBounding, roundSetup["bounding-box"], roundSetup["oldest-year"])

    return streetViewPoints, mapMeta, mapImgs

def handleClickEvent(event, mapImg, streetViewLoc):
    global clickLocs
    currentTime = time.time()
    clickLocs.append([event.xdata, event.ydata, currentTime])
    if len(clickLocs) > 1:
        tElapsed = currentTime - clickLocs[-2][2]
        dist = calculateDistance(clickLocs[-1][:2], clickLocs[-2][:2])
        
        if (tElapsed < 0.5) and (dist < 10):
            if [0,0,0] in clickLocs:
                plt.close()
            else:
                clickLocs.append([0,0,0])
                streetViewCoords = mapImg.getPixelCoords(streetViewLoc)
                plt.scatter(event.xdata, event.ydata, c="blue")
                plt.scatter(streetViewCoords[0], streetViewCoords[1], c="green")
                plt.show()

                userCoords = [event.xdata,event.ydata]
                dist = calculateDistance(streetViewCoords, userCoords) * mapImg.pixelsPerMeter
                print(f"You where {round(dist):,}m away from the correct location")
