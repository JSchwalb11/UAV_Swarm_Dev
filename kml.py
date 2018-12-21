from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from lxml import etree
from decimal import *
import argparse
import csv
import os.path



def Main():
   parser = argparse.ArgumentParser(description='This is a tool for converting DroneBrain CSV dumps to a user friendly KML file.')
   parser.add_argument("input", help="The CSV file you wish to convert", type=str)
   parser.add_argument("output", help="The desired output file location", type=str)
   parser.add_argument("-q", "--quality", help="An integer to represent the interval between points. eg. Imagine it as a divider, if 2 is chosen half the points will be processed. Default: 1", default=1)
   parser.add_argument("-sa", "--startingAltitude", help="The actual starting altitude of the vehicle. Useful if using in a sitl environment as the value fed in for ground will not be perfectly accurate, Unit: FEET")



   args = parser.parse_args()

   if not os.path.isfile(args.input):
      print "Error, file does not exist. Exiting."
      exit()

   try:
      quality = int(args.quality)
   except ValueError:
      print "Value of quality is of type integer. Exiting."
      exit()


   if not (args.startingAltitude == None):
      convertToKML(args.input, args.output, int(quality), startingAltitude=float(args.startingAltitude), needOffsetAlt=True)
   else:
      convertToKML(args.input, args.output, int(quality))
      

def convertToKML(inFile, outFile, quality, startingAltitude=0, needOffsetAlt=False):


   placemarks = []
   linePoints = []
   time_start = -1



   with open(inFile, 'r') as csv_file:
      reader = csv.reader(csv_file)
      dt = 0
      for idx, field in enumerate(reader):
         if idx == 0:
            time_start = float(field[0])
            if needOffsetAlt == True:
               offsetFt =  float(startingAltitude) - float(field[3])
               offsetM = ftToM(offsetFt)
            else:
               offsetM = 0


         if (idx % quality == 0): 
            altitude = ftToM(field[3]) + offsetM
            dt = float(field[0]) - time_start
            linePoints.append(field[2] + "," + field[1] + "," + str(altitude) + " ")

            placemarks.append(
               KML.Placemark(
                  KML.name(Decimal(dt).quantize(Decimal(10) ** -2)),
                  KML.description(field[0]),
                  KML.Point(
                     KML.altitudeMode("absolute"),
                     KML.coordinates(
                        field[2] + "," + field[1] + "," + str(altitude)
                     )
                  )
               )
            )

         

   km = KML.kml()
   doc = KML.Document()
   pointFolder = KML.Folder(
      KML.name("Point Folder"),
      KML.description("Contains each individual point along the route.")
   )


   #Create a style to add to the line

   style = KML.Style(
      KML.LineStyle(
         KML.color("7f00ffff"),
         KML.width("4")
      ),
      KML.PolyStyle(
         KML.color("7f00ff00")
      ),
      id="yellowLineGreenPoly",
   )

   #Create the line
   bigString = ""
   for point in linePoints:
      bigString = bigString + point

   line = KML.LineString(
      KML.extrude("1"),
      KML.tessellate("1"),
      KML.altitudeMode("absolute"),
      KML.coordinates(bigString)
   )

   linePlacemark = KML.Placemark(
      KML.name("Flight Path"),
      KML.description("The flight path of the vehicle"),
      KML.styleUrl("#yellowLineGreenPoly")
   )

   linePlacemark.append(line)

   for pm in placemarks:
      pointFolder.append(pm)

   doc.append(style)
   doc.append(linePlacemark)
   doc.append(pointFolder)
   km.append(doc)
   

   kmlBuffer = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(km, pretty_print=True)
   outputFile = open(outFile, "w+")
   outputFile.write(kmlBuffer)
   outputFile.close()
   

def ftToM(inFt):
   return float(inFt) * .3048

if __name__ == '__main__':
   Main()