import csv

import gizeh
import moviepy.editor as mpy
with open('csvtest', 'w') as csv:
    for i in range(0, 10):
        csv.write(str(i) + ',' + str(i * 10) + '\n')

with open('drone1_log', 'r') as logfile:
    pos = []
    for idx, line in enumerate(logfile):
        #print(idx)
        data = line.split(',')
        #pos.append(data.trim)
        print(data)



W,H = 128,128 # width, height, in pixels
fps = 15
duration = 2 # duration of the clip, in seconds

def make_frame(t):
    #print(t)
    print(t * fps)
    surface = gizeh.Surface(W,H)
    radius = 20 #W*(1+ (t*(duration-t))**2 )/6
    circle = gizeh.circle(radius, xy = (fps * t * 4, H/2), fill=(1,0,0))
    circle.draw(surface)
    return surface.get_npimage()

clip = mpy.VideoClip(make_frame, duration=duration)
clip.write_gif("circle.gif",fps=fps, opt="OptimizePlus", fuzz=10)
"""
import moviepy.editor as mpy
from PIL import Image, ImageDraw


def getFrame(t):
    print(t)
    image = Image.new("RGB", (200,200), (255,255,255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((20, 20, 180, 180), fill='blue', outline='blue')
    return image

clip = mpy.VideoClip(getFrame, duration=2)

"""