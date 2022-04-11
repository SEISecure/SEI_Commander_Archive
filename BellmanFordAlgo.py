import csv
import math
#create the map file
endPointIsNotUpdated = True
timeWithoutChange = 0
#starts at rocky cliff
StartX = 11 #12th index 
StartY = 17 # 18th index 

#Ends at a forest
EndX = 13 #14th index 
EndY = 22 #21st index 

#################################################
###Make weight change for user discretion########
#################################################
infilCoverWeight = 1
infilConcealmentWeight = 2


terrainConcealment = [0.0,0.0,1.0,0.5,0]
terrainCover = [0.0,0.0,1,0.5,0.5]
landTerritory = []
for i in range (0, 31):
    temp = []
    for j in range(0, 34):
        temp.append(0)
    landTerritory.append(temp)

# weight will use for Belman Ford Shortest Path
pathWeight = []
for i in range (0, 31):
    temp = []
    for j in range(0, 34):
        temp.append(10000.0)
    pathWeight.append(temp)

pathWeight[StartY][StartX]=0 #define path 


#read in map file
with open('C:\Users\RoyPC\Documents\ONR BAA\Submital Folder\ONR Project\ONR Map.csv') as csvfile:
    mapreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    mapYindex = 0
    for row in mapreader:
       
        mapXindex = 0
        for value in row:
            landTerritory[mapYindex][mapXindex] = int(value)
            mapXindex +=1
        mapYindex += 1

xWeightUpdate =[StartX]
yWeightUpdate = [StartY]
updatedBy =[0]

endNodeIndex=0

#update weight
while (endPointIsNotUpdated or timeWithoutChange<10):
    if endPointIsNotUpdated == False:
        timeWithoutChange+=1
    for i in range(0, len(xWeightUpdate)):
        x = xWeightUpdate[i]
        y = yWeightUpdate[i]
        
        for t in range (-1, 2):
            for v in range (-1, 2):
                if (x+t) >= 0 and (x+t)<34 and (y+v) >= 0 and (y+v)<31 and (abs(t)+abs(v)) != 0: #is the location within the map and not the current patch. You cannot update the distance of the currently selected patch
                    
                    distance = math.sqrt( (abs(t) + abs(v))*1.0)
                    concealmentWeight = infilConcealmentWeight - infilConcealmentWeight*terrainConcealment[landTerritory[y+v][x+t]] 
                    coverWeight = infilCoverWeight - infilCoverWeight*terrainCover[landTerritory[y+v][x+t]] 
                    
                    newWeight = pathWeight[y][x] + distance + concealmentWeight + coverWeight
                    if newWeight < pathWeight[y+v][x+t] and ( (y+v) != StartY or (x+t) !=StartX): #did the weight improve and this is not the start node.
                        pathWeight[y+v][x+t] = newWeight
                        xWeightUpdate.append(x+t)
                        yWeightUpdate.append(y+v)
                        updatedBy.append(i)
                        if (y+v) == EndY and (x+t) ==EndX:
                            endNodeIndex = len(yWeightUpdate)-1
                            endPointIsNotUpdated=False
                            timeWithoutChange =0
  
  
print str(xWeightUpdate[endNodeIndex]) +"," + str(yWeightUpdate[endNodeIndex]) +","+ str(landTerritory[yWeightUpdate[endNodeIndex]][xWeightUpdate[endNodeIndex]])
previousNode = updatedBy[endNodeIndex]

while previousNode != 0:
    print str(xWeightUpdate[previousNode]) +"," + str(yWeightUpdate[previousNode])+","+ str(landTerritory[yWeightUpdate[previousNode]][xWeightUpdate[previousNode]])
    previousNode = updatedBy[previousNode]
print str(xWeightUpdate[previousNode]) +"," + str(yWeightUpdate[previousNode]) +","+ str(landTerritory[yWeightUpdate[previousNode]][xWeightUpdate[previousNode]])
                
#record the squares that updated
#termination criteria met








