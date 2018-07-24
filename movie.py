import csv
import gizeh
import moviepy.editor as mpy
from PIL import Image, ImageDraw

with open('drone1_csv', 'r') as logfile:
    pos = []
    for idx, line in enumerate(logfile):
        data = line.split(',')
        print(data)



W,H = 128,128 # width, height, in pixels
fps = 60
duration = 0.5 # duration of the clip, in seconds

def make_frame(t):
    #print(t)
    print(t * fps)
    surface = gizeh.Surface(W,H)
    radius = 20 #W*(1+ (t*(duration-t))**2 )/6
    circle = gizeh.circle(radius, xy = (fps * t * 4, H/2), fill=(1,0,0))
    circle.draw(surface)
    return surface.get_npimage()

clip = mpy.VideoClip(make_frame, duration=duration)
clip.write_videofile("circle.mp4",fps=fps)

def getFrame(t):
    print(t)
    image = Image.new("RGB", (200,200), (255,255,255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((20, 20, 180, 180), fill='blue', outline='blue')
    return image

clip = mpy.VideoClip(getFrame, duration=2)