import csv



def getTerrainFromFile(fileName):
    terrain = {}
    with open(fileName+'.csv', 'rt') as f:
        reader = csv.reader(f)
        print("Reading Terrain Data")
        for row in reader:
            terrain[float(row[0]),float(row[1])] = float(row[2]), float(row[3]),float(row[4])
        print("Done")
    return terrain

def getCoverOrConcealmentFromFile(fileName):
    terrain = {}
    with open(fileName+'.csv', 'rt') as f:
        reader = csv.reader(f)
        print("Reading Cover/Concealment Data")
        for row in reader:
            terrain[float(row[0]),float(row[1])] = float(row[2])
        print("Done")
    return terrain    
    
def getVisFromFile(fileName):
    visibility = {}
    visited = {}
    index = 0 #index used to skip header
    with open(fileName+'.csv', 'rt' ) as f:
        #headers = ['unit_x', 'unit_y', 'target_x', 'target_y', 'visible']
        reader = csv.reader(f)
        print("Reading Visibility Data")
        for row in reader:
            if (index == 1):
                if((float(row[0]),float(row[1]), float(row[2]), float(row[3])) not in visibility):
                    visibility[float(row[0]),float(row[1]), float(row[2]), float(row[3])] = float(row[4])
                    visited[float(row[0]),float(row[1])] = 0
                    visited[float(row[2]), float(row[3])] = 0
                if((float(row[0]),float(row[1]), float(row[2]), float(row[3]))  in visibility and visibility[float(row[0]),float(row[1]), float(row[2]), float(row[3])] >=0.99 ):
                    visibility[float(row[0]),float(row[1]), float(row[2]), float(row[3])] = float(row[4])
                    visited[float(row[0]),float(row[1])] = 0
                    visited[float(row[2]), float(row[3])] = 0
            else:
                index = 1
        print("Done")
    return visibility, visited    
  
def generateConcealmentFromFile(fileName):
    with open(fileName+'.csv', 'rt') as f:
        reader = csv.reader(f)
        print("Reading Concealment Data")
        for row in reader:
            saveToConcealmentFile(fileName, float(row[0]),float(row[1]), float(row[3]))
        print("Done")
    
    
def saveToConcealmentFile(fileName, x, z, terrainType):
    with open(fileName+'_Concealment.csv', mode ='a', newline='') as csv_file:   
        #headers = ['X', 'Z', 'open', 'closed', 'neighbors', 'DToPath', 'ElevationChange']
        writer = csv.writer(csv_file)
        tType = 0
        if(terrainType == 1 or terrainType == 4 ):
            tType = 1
        row = [x,z, tType]
        #if csv_file.tell() == 0:
            #writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow(row)
        print("Concealment Row Written")      
  
    
def generateCoverFromFile(fileName):
    with open(fileName+'.csv', 'rt') as f:
        reader = csv.reader(f)
        print("Reading Cover Data")
        for row in reader:
            saveToCoverFile(fileName, float(row[0]),float(row[1]), float(row[3]))
        print("Done")   
'''
minX = 1800
minY = 10100
maxX = 2200
maxY = 10900
'''
def addToVisFile(fileName, min_X, max_X, min_Y, max_Y): 
    #op_min_X = 1800
    #op_max_X = 2200
    #op_min_Y = 10100
    #op_max_Y = 10900   
    with open(fileName+'.csv', mode ='a', newline='') as f:
        writer = csv.writer(f)
        for x in range (min_X, (max_X + 20), 20):
            for y in range (min_Y, (max_Y + 20), 20):
                for op_x in range (min_X, (max_X + 20), 20):
                    for op_y in range (min_Y, (max_Y + 20), 20):
                        row = [x, y, op_x, op_y]
                        print(row)
                        writer.writerow(row)
    
def saveToCoverFile(fileName, x, z, terrainType):
    with open(fileName+'_Cover.csv', mode ='a', newline='') as csv_file:   
        #headers = ['X', 'Z', 'open', 'closed', 'neighbors', 'DToPath', 'ElevationChange']
        writer = csv.writer(csv_file)
        tType = 0
        if(terrainType == 4 ):
            tType = 1
        row = [x,z, tType]
        #if csv_file.tell() == 0:
            #writer.writeheader()  # file doesn't exist yet, write a header
        writer.writerow(row)
        print("Cover Row Written")    
    
    
def getDangerAreaFromFile(fileName):
    terrain = {}
    assaultedArea = []
    with open(fileName+'.csv', 'rt') as f:
        reader = csv.reader(f)
        print("Reading Danger Area Data")
        i = 0
        for row in reader:
            terrain[float(row[0]),float(row[1])] = float(row[2]), i
            i = i + 1
        print("Done  ", len(terrain))
        
        assaultedArea = [False]*len(terrain)
    return terrain, assaultedArea
