'''This code is used in canyon environments and is used to predict the most tarveled waypoints.
It runs using a Arma3 print of the map. You must have the Arma 3 text file in a repository, where it is the only text file

'''
import spotCanyon
import math
import copy
import sys
import copy
import random
import glob
import os
import time

class Astar(object):
 

    def __init__(self):
        path = 'D:/SWAT-C Dahlgren/'
        path2 = 'C:/arma3/terrain/'
        time.sleep(10)
        self.goalLocation = {}
        self.startNode=None
        self.solutionFound=False
        self.openSet = []
        self.closesLong =0
        self.closesLat = 0
        self.closeSet =[]
        self.navPoints = {}
        self.Obstacles = ['leaf_pines', 'cargo', 'wf_hesco', 'c_thistle_high']
        # Gets all text files in a directory
        textFile = glob.glob(path2+"*.txt")
        #Opens the only text file in the directory that specifies the playing area
        #the file will give coordinates, as well as obstacles at the coordinates
        lOfNavpoints = open(textFile[0], 'r')
        listOfNavpoints = lOfNavpoints.readlines()
        for point in listOfNavpoints:
            
            notPassable = 0
            for obstacle in self.Obstacles:
                if obstacle in point:
                    notPassable = 1

            pointVal = point.split(' ')
            if "trig_1" in  point:
                trigName = pointVal[2].replace('[', '')
                trigName = trigName.replace(']', '')
                trigName = trigName.strip()
                self.goalLocation["trig_1"]= (int(pointVal[0]),int(pointVal[1]))
                
            elif "trig_2" in  point:
                trigName = pointVal[2].replace('[', '')
                trigName = trigName.replace(']', '')
                trigName = trigName.strip()
                self.goalLocation["trig_2"]= (int(pointVal[0]),int(pointVal[1]))
            #print(pointVal)
            pointName = (int(pointVal[0]),int(pointVal[1]))
            tempSpot = spotCanyon.spot()
            
            tempSpot.setXY(float(pointVal[0]),float(pointVal[1]))
            tempSpot.setName(pointName)
            
            tempSpot.setAttributes(notPassable)
            self.navPoints[pointName] = copy.deepcopy(tempSpot)
        #print(self.navPoints.keys())
       
        
        # runs through all nav points and checks the 8 neighbors
        # first determines if the point is in the the list of nav points
        # Then  assess if the poit is passable. 1 = Not passable
        for pointName in self.navPoints.keys():
            currentSpot = self.navPoints[pointName]
            currentPointX = pointName[0]
            currentPointY = pointName[1]
            if currentSpot.getNotPassable() == 0:
                for i in range(-1, 2):
                    for j in range (-1, 2):
                        if i != j:
                            tempTuple = (i+currentPointX,j+currentPointY)
                            if tempTuple in self.navPoints:
                                potentialNeighbor = self.navPoints[tempTuple]
                                if potentialNeighbor.getNotPassable() ==0:
                                    currentSpot.addNeighbor(self.navPoints[tempTuple])

            
        
        

    def defineStartNode(self,startX,startY):
        distance =10000
        for spot in self.navPoints.keys():
            
            x,y = self.navPoints[spot].getXY()
            tempDistance = math.sqrt(math.pow((x-startX),2)+ math.pow((y - startY),2))
            if tempDistance <distance:
                distance = tempDistance
                self.startNode = self.navPoints[spot]
              
        
        self.openSet.append(self.startNode)
    
    def defineEndNode(self,endX,endY):
        distance =10000
        for spot in self.navPoints.keys():
            
            x,y = self.navPoints[spot].getXY()
            tempDistance = math.sqrt(math.pow((x-endX),2)+ math.pow((y - endY),2))
            if tempDistance <distance:
                distance = tempDistance
                self.closesLong =x
                self.closesLat = y
        
    def reset(self):
        
        for points in self.navPoints.keys():
            self.navPoints[points].clearGHFScore()
            self.navPoints[points].clearPreviousSpot()
        self.openSet = []
        self.closeSet =[]
        self.closesLong =0
        self.closesLat = 0

    
    def getGoalLocation(self):
        return self.goalLocation
        

    def getRandomPath(self, endLocTuple):  
        #print("start")      
        navPointName = list(self.navPoints.keys())
        #print("start-1")
        randomStartPoint = navPointName[random.randint(0,len(navPointName)-1)]
        #print("start-2")
        #print("Random Start", randomStartPoint[0], randomStartPoint[1] )
        #print("End", endLocTuple[0],endLocTuple[1])
        #print(endLocTuple)
        #print(randomStartPoint)
        route = self.aStarPerform(randomStartPoint[0], randomStartPoint[1], endLocTuple[0],endLocTuple[1])
        if None == route:   
            return []
        
        return route 
   
    def getPreviousNode(self, previousSpotName):
        
        namePreviousSpot= [previousSpotName]
        
            
        while previousSpotName != None:
            previousSpotName =self.navPoints[previousSpotName].getPreviousSpot()
            if previousSpotName!= None:
                namePreviousSpot.append(previousSpotName)
        #print(namePreviousSpot)

        route =[]
        for i in range (len(namePreviousSpot)-2,-1,-1):#iterate through the list backwards skipping inital starting location
            long,lat = self.navPoints[namePreviousSpot[i]].getXY()
            heading =0
            route.append((lat,long,heading))
        #route.append((endLat,endLong,0))
        #print(route)
        
        waypointRoute=[]
        for i in range (len(namePreviousSpot)-1,-1,-1):#iterate through the list backwards 
            waypointRoute.append(namePreviousSpot[i])
            
        return  waypointRoute
    
            
    def aStarPerform(self,startLong, startLat, endLong,endLat):
        #print("hi-1")
        self.reset()
        #print("hi-2")
        
        self.defineStartNode(startLong,startLat)
        #print("hi-3")
        self.defineEndNode(endLong,endLat)
        #print("hi-4")
        while len(self.openSet)>0:
            lowestFscore =3000000
            lowestLat =0
            lowestLong = 0
            indexLoc = 0
            t = 0
            #print("here-1")
            lowstFSpot=None
            for spot in self.openSet:#itereates through the open set
                if spot.getFscore()<lowestFscore: #finds the spot witht the lowest F score
                    lowestFscore = spot.getFscore() # gets Fscore
                    lowestLong,lowestLat  = spot.getXY() #gets lat and long
                    indexLoc = copy.deepcopy(t)
                    lowstFSpot=spot
                t=+1
            #print("here-2")
            if lowestLat == self.closesLat and lowestLong== self.closesLong: #reached the destination stop
                #print("here-3")
                return self.getPreviousNode(lowstFSpot.getName())
                solutionFound = True
                break
            
            self.closeSet.append(lowstFSpot) #adds position to closetSet
            self.openSet.pop(indexLoc) #removes current Position from Openset
            #find neighbors for north,south, east west
            getNeighbors = lowstFSpot.returnNeighbor() # get all neighbors 
            neighborName = lowstFSpot.getName() # get x.y of neighbor
            #print("here-4")
            lowestFSpotXY = lowstFSpot.getXY()
            for neighbor in getNeighbors:# for each neighbor
                
                neighSpot = self.navPoints[neighbor.getName()]
                if neighSpot not in self.closeSet:
                    gAddition = neighSpot.calculateGAddition(lowestFSpotXY[0],lowestFSpotXY[1])
                    tenativeG = lowstFSpot.getGscore() +gAddition # create a tentiative G
            
                    currentG = neighSpot.getGscore() #get currentG
                    neighSpot.calculateH(endLong,endLat) #calculate H score
                    if currentG > tenativeG or currentG == 0: # if current G is greater than tenative G or = 0
                       
                        neighSpot.setGscore(tenativeG, neighborName) # replace g score and marke previous
                        neighSpot.calculateFscore() #recalculate F score
                        self.openSet.append(neighSpot) # add neighbor to open set 
                        
                        self.navPoints[neighbor.getName()]  = neighSpot #replace grid location with updated neighbor spot
            






'''
test = Astar()
#funct1- identify nearest goal location for a specified ugv stomper
#funct2- identify the most traversed waypoint for both goals make a ugv sit there
#objectives r trig_1 and trig_2
#startLat = 34.407706
#startLong = -116.2768105
#endLat = 34.4082598
#endLong = -116.274605
#startLat = 38.575065
#startLong = -77.547101
#endLat= 38.574117
#endLong=  -77.544848
#Astar.reset()
#locations = test.aStarPerform(startLong, startLat, endLong,endLat)
#print(locations)

traversedPoints = {}
routePaths ={}
output =''
time = 0
while  time < 1:
   
    
    #while startLat==0 or (startLat<38.574675 and startLong< -77.544824 ):
    #    startLat = random.uniform(38.573214, 38.575980)
    #    startLong =random.uniform(-77.543503, -77.546606)
    

    #woods 
    #startLat = random.uniform(38.573500, 38.574009)
    #startLong =random.uniform(-77.547450, -77.544974)

    #likely army starting location
    #startLat = random.uniform(38.574374, 38.575616)
    #startLong =random.uniform(-77.546736,-77.546262)
    
    #Navy Side
    #startLat = random.uniform(38.573214, 38.574677)
    #startLong =random.uniform(-77.543885,-77.543503)

    #midMap

    #possibleStartLat =[38.315745,38.308247,38.295189,38.293674,38.309715]
    #possibleStartLong =[-77.057314,-77.056838,-77.052381,-77.050863,-77.031743]
    #tempI = random.randint(0, (len(possibleStartLat)-1))
    startLat = 574
    startLong = 360
    

    #endLat= 0
    #endLong=  0
    #while endLat==0 or (endLat<38.574675 and endLong< -77.544824 ):
    #    endLat = random.uniform(38.573214, 38.575980)
    #    endLong =random.uniform(-77.546606,-77.543503)

    
    possibleEndLat =[38.306836,38.303930,38.294836]
    possibleEndLong = [-77.045980,-77.034806,-77.049467]
    tempI = random.randint(0, (len(possibleEndLat)-1))
    endLat= 0
    endLong=  0
    otherLat=[]
    otherLong=[]
    #Attack Ending Position
    for i in range(0,len(possibleEndLat)):
        if i == tempI:
            endLat= possibleEndLat[i]
            endLong=  possibleEndLong[i]
        else:
            #other enemy stronghold locations
            otherLat .append(possibleEndLat[i])
            otherLong.append(possibleEndLong[i])
    

    endLat= 624
    endLong=  645
        
    
    

    
    locations = test.aStarPerform(startLong, startLat, endLong,endLat)
    pathStr=''
    if None != locations :
        time+=1
        output = ""
        for loc in locations:
            output+=','+str(loc)
            pathStr+=str(loc)+','
        pathStr=pathStr[:-1]
        
        if pathStr in routePaths:
            routePaths[pathStr] = routePaths[pathStr] + 1
        else:
            routePaths[pathStr] = 1
        output+='\n'
        output=output[1:]
        for i in range( 1 , len(locations)-1):
            if locations[i] in traversedPoints:
                traversedPoints[locations[i]] +=1
            else:
                traversedPoints[locations[i]] =1

f = open('D:/Code Repository/attackTrajecotires.csv', 'w')
outPoints=''
for key in routePaths:
    outPoints+= str(routePaths[key])+','+str(key)+'\n'
outPoints = outPoints[:-1]
f.write(outPoints)


f = open('D:/SWAT-C Dahlgren/trajectories.txt', 'w')
f.write(output)
f.close()


outPoints ='waypoint, count \n'
for key in traversedPoints:
    outPoints+= str(key)+','+str(traversedPoints[key])+'\n'
outPoints = outPoints[:-1]


g = open('D:/Annapolis/mostTraversedPoints.csv', 'w')
g.write(outPoints)
'''