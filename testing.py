from matplotlib import pyplot as plt
from matplotlib.image import imread
import time

clickLocs = []

def calculateDistance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5


def onclick(event):
    global clickLocs
    currentTime = time.time()
    clickLocs.append([event.xdata, event.ydata, currentTime])
    if len(clickLocs) > 1:
        tElapsed = currentTime - clickLocs[-2][2]
        dist = calculateDistance(clickLocs[-1][:2], clickLocs[-2][:2])
        if (tElapsed < 0.5) and (dist < 10):
            plt.close()

# Render Image itself
verLabel = 2
imgNumber = 1
imgPath = f"./data/maps/kozi/{verLabel}/{imgNumber}.png"

image = imread(imgPath)

fig = plt.figure()
ax = fig.add_subplot()

cid = fig.canvas.mpl_connect('button_press_event', onclick)

ax.imshow(image)
plt.grid(False)
plt.axis('off')
plt.show()


