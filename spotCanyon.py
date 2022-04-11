import math
class spot(object):
    
   
    def __init__(self):
    
        self.g = 0
        self.h = 0
        self.f = 0
        self.x = 0
        self.y = 0
        self.Name =''
       
        self.NotPassable =0
        
        #provides weights that will increase or decrease weight of route
        
        self.previousNode = None
        self.Neighbors = []
        self.cornerNeighbors =[] # neighbors on the for corners

    def setName(self,spotName):
        self.Name = spotName
    
    def setMinDistanceOtherStrongHold(self, targetX, targetY):
        dis = 10000
        for i in range(0, len(targetX)):
            tempDis = abs(targetX[i]-self.x )+abs(targetY[i]-self.y)
            if tempDis<dis:
                dis=tempDis
        self.distancetoOtherEnemyStronghold =dis


    def setAttributes(self, NotPassable):
        self.NotPassable = NotPassable
       
    
    def getName(self):
        return self.Name
    def clearGHFScore(self):
        self.g=0
        self.h =0
        self.f=0
    def setGscore (self, tentativeG, previousNeighbor ):
        self.g  =  tentativeG
        self.previousNode = previousNeighbor
    
    def getNotPassable(self):
        return self.NotPassable
        
    def getGscore(self):
        return self.g

    def setHscore (self, double):
        self.s = double

    def getHscore(self):
        
        return self.h

    def setXY(self, i, j):
        
        self.x = i
        self.y = j

    def getXY(self):
        
        return (self.x, self.y)
        
    def calculateFscore(self):
        
        self.f = self.g + self.h

    def calculateGAddition (self, previousX, previousY):
        return ( math.sqrt(math.pow((previousX-self.x),2)+ math.pow((previousY - self.y),2) ))

    def calculateH(self, endX, endY):
        Distance = math.sqrt(math.pow((endX-self.x),2)+ math.pow((endY - self.y),2))*10 
        self.h=Distance
        #self.h = abs(endX-self.x)+ abs(endY - self.y)

    def getFscore(self):
      
        return self.f

    def clearPreviousSpot(self):
        self.previousNode = None
    
    def getPreviousSpot(self):
        
        return self.previousNode

    def addNeighbor(self, neighborSpot):
       
        self.Neighbors.append(neighborSpot)
    
    def addNeighbor(self, neighborSpot):
       
        self.Neighbors.append(neighborSpot)

    def addCornerNeighbor(self, neighborSpot):
       
        self.cornerNeighbors.append(neighborSpot)
    
    def setBuildingTrue(self):
        self.building = 1

    def isBuildingPresent(self):
        return self.building
    
    def returnNeighbor(self):
       
        return self.Neighbors
    
    def returnCornerNeighbor(self):
       
        return self.cornerNeighbors



