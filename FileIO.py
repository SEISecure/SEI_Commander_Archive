import csv
import math




def getForestFromTerrainFile(fileName): 
    forests = {}
    with open(fileName+'.csv', 'rt') as f:
        header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        print("Reading Forest Data")
        for row in reader:
            forests[float(row[1]),float(row[3])] = [float(row[6])]
        print("Done")
    return forests

def getElevationFromFile(fileName):
    foundindex = -1
    elevations = {}
    with open(fileName+'.csv', 'rt') as f:
        #header = next(f).strip("\n").split(",")
        print("Reading Elevation Data")
        reader = csv.reader(f)
        zCoordinates = next(reader) 
        #results = filter(lambda x: x[0] , reader)
        for row in reader:
            for zpos in range(0,len(zCoordinates)):
                if(zCoordinates[zpos] != ''):
                    #print(row[zpos])
                    elevations[int(float(row[0])),int(float(zCoordinates[zpos]))] = float(row[zpos])
        print("Done")       

    return elevations


def getElevationFromFileVBS4(fileName):
    elevations = {}
    with open(fileName+'.csv', 'rt') as f:
        header = next(f).strip("\n").split(",")
        reader = csv.reader(f)
        print("Reading Elevation Data")
        for row in reader:
            elevations[float(row[1]),float(row[2])] = float(row[3])
        print("Done")
    return elevations



def getElevationAtLocationFromFile(fileName, X, Z):
    elevation = 0
    foundindex = -1
    with open(fileName+'.csv', 'rt') as f:
        #header = next(f).strip("\n").split(",")

        reader = csv.reader(f)
        zCoordinates = next(reader) 
        results = filter(lambda x: x[0]==str(roundup(float(X))), reader)
        #results = filter(lambda x: x[0] , reader)
        for zpos in range(0,len(zCoordinates)):
            if(zCoordinates[zpos] != ''): 
                if(int(float(zCoordinates[zpos])) == roundup(float(Z))):
                    foundindex = zpos
        for line in results:
            elevation = float(line[foundindex])
            #print(elevation)
    return elevation

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10