import json
import math
import cliFunc as cli
from appFunc import establishSetup, colors, showAppSetup, loadData, handleClickEvent
from geoManager import getMap
import webbrowser
import random
from matplotlib import pyplot as plt
from matplotlib.image import imread


# Random Constants
version = "0.0.1"
clickLocs = []

# Load Setup data
with open("./data/setup.json", "r") as setupFile:
    appSetup = json.load(setupFile)

if appSetup["metaData"]["version"] != version:
    print(f"{colors.WARNING}WARNING - Setup File Version Mismatch\nThe version of the setupfile ({appSetup["metaData"]["version"]}) is different to the version of the app ({version}). This may cause errors{colors.ENDC}")


# Print Welcome stuff
logo = r"""   
  ____            _                      ____                          
 / ___|___  _ __ | |_ ___  _   _ _ __   / ___|_   _  ___  ___ ___ _ __ 
| |   / _ \| '_ \| __/ _ \| | | | '__| | |  _| | | |/ _ \/ __/ __| '__|
| |__| (_) | | | | || (_) | |_| | |    | |_| | |_| |  __/\__ \__ \ |   
 \____\___/|_| |_|\__\___/ \__,_|_|     \____|\__,_|\___||___/___/_|   
 
"""
print(f"{logo}Version {version}")
print(f"Developed by Gabriel Hanich\n")

roundSetup = appSetup["setups"][cli.selectListElem("Select the game format", list(appSetup["setups"].keys()))]
establishSetup(roundSetup)


streetViewLocs, mapMeta, mapImgs = loadData(roundSetup)

print(f"{colors.OKGREEN}Successfully loaded all necessary files{colors.ENDC}")

# Calculate the valid streetview locations


showAppSetup(roundSetup, streetViewLocs, mapMeta)

# if input("Do you want to start? (Y/n)").lower() not in ["", "y", "yes"]:
#     exit()

# Generate a list of random numbers to serve as indexes for the location
random.seed(roundSetup["seed"])
locIndex = list(math.floor(random.random() * len(streetViewLocs)) for _ in range(roundSetup["rounds"]))

for roundNumber in range(roundSetup["rounds"]):
    print(f"Round {roundNumber + 1}")
    print("Look at the google street view, then open the map and double-click on where you think you are")
    
    thisLoc = streetViewLocs[locIndex[roundNumber - 1]]
    thisMap = getMap(thisLoc, mapImgs)
    url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={thisLoc.lat},{thisLoc.long}"
    clickLocs = []

    
    webbrowser.open(url)
    pngData = imread(f"./data/maps/{roundSetup['map']}/{roundSetup['map-version']}/{thisMap.id}.png")
    fig = plt.figure()
    ax = fig.add_subplot()
    cid = fig.canvas.mpl_connect('button_press_event', (lambda x : handleClickEvent(x, thisMap, thisLoc)))

    ax.imshow(pngData)
    plt.grid(False)
    plt.axis('off')
    plt.show()

