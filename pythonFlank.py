## this function provides the flanking position for a fix and flank
#once we decide to perform a flank we need to find and X,Z location that is the flank location
# to do this we first find the line of best fit that goes through the visible enemies 
# We then find the closest X,Z location that is on the line of best fit
# we will then move a unit to perform the flank.

#provide x and z of enemy 
xEnemy = [1, 2, 3, 4, 5]
zEnemy = [1, 2, 3, 4 ,5]

#provide x and z of fireteam 
xTeam = [3, 3.1, 3.3, 3.6]
zTeam = [4, 4, 4, 4]
def flankPosition (xEnemy, zEnemy, xTeam, zTeam):
    #gets the average X and y of enemy
    averageX = 0.0
    averageX = sum(xEnemy)/len(xEnemy)
    averageZ = 0.0
    averageZ = sum(zEnemy)/len(zEnemy)


    #finds the slope of the line of best fit
    slope = 0.0
    squared=0.0
    for i in range(len(xEnemy)):
        slope+= (xEnemy[i]-averageX) * (zEnemy[i]-averageZ)
        squared+=(xEnemy[i]-averageX) * (xEnemy[i]-averageX)
    slope = slope/squared
    del squared

    b = averageZ - slope*averageX


    #calcualate average X and Z of the friendly fireteam
    friendlyAvgX = sum(xTeam)/len(xTeam)
    friendlyAvgZ = sum(zTeam)/len(zTeam)

    slopeIntesectingLine = -1*1/slope
    bIntersectingLine = friendlyAvgZ - slopeIntesectingLine * friendlyAvgX

    flankingX = (bIntersectingLine - b)/(slope - slopeIntesectingLine)
    flankingZ = slopeIntesectingLine*flankingX + bIntersectingLine
    return [flankingX,flankingZ]
    

print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))