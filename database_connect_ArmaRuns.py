import psycopg2
import numpy as np
import pandas as pd


connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")
'''
connection = psycopg2.connect(user = "postgres",
                                  host = "192.168.1.61",
                                  port = "5432",
                                  database = "units")
'''
#credentials = "postgresql://postgres:ichigo@192.168.1.61:5432/units"


def armaRunData(runNumber, time, opfor_dead, bluefor_dead, blue_sent_location_x, blue_sent_location_y, percentBuddyTeamVisibleRange, minCover,
                 minConcealment, averageCover, averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, areaLeftUnsearched, distanceMoved):
    cursor = connection.cursor()
    preparedStatement = "insert into armaruns (runNumber, timestamp, opfor_remaining, bluefor_remaining, blue_sent_location_x, blue_sent_location_y, percentBuddyTeamVisibleRange, \
    minCover, minConcealment, averageCover, averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, areaLeftUnsearched, distanceMoved) \
     values ('" + str(runNumber) + "','" + str(time) + "','" + str(opfor_dead) +  "','" + str(bluefor_dead) + "','"+ str(blue_sent_location_x) + "','" + str(blue_sent_location_y) + "','" \
     + str(percentBuddyTeamVisibleRange) +  "','" + str(minCover) + "','" + str(minConcealment) + "','" + str(averageCover) + \
      "','" + str(averageConcealment) + "','" + str(averageVisibleArea) + "','" + str(percentBuddyTeamNotMoving) + \
       "','" + str(largestNumberBuddyTeam30Meters) + "','" + str(areaLeftUnsearched) + "','" + str(distanceMoved) +  "');"
    cursor.execute(preparedStatement)
    connection.commit()
    
def getNumberofRuns():
    cursor = connection.cursor()
    cursor.execute("select count(runNumber) from armaruns;")
    count = cursor.fetchone()
    return int(count[0])

def getNumberofWeights():
    cursor = connection.cursor()
    cursor.execute("select count(percentBuddyTeamVisibleRange) from GeneratedWeigths;")
    count = cursor.fetchone()
    return int(count[0])


def insertWeights(weight_percentBuddyTeamVisibleRange,
weight_minCover,
weight_minConcealment,
weight_averageCover,
weight_averageConcealment,
weight_averageVisibleArea,
weight_percentBuddyTeamNotMoving, 
weight_largestNumberBuddyTeam30Meters,
weight_areaLeftUnsearched,
weight_distanceMoved ):

    cursor = connection.cursor()
    soldier1Move = "insert into GeneratedWeigths (percentBuddyTeamVisibleRange, minCover, minConcealment, averageCover, \
     averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, \
areaLeftUnsearched, distance)  values ('" + str(weight_percentBuddyTeamVisibleRange) + "','" + str(weight_minCover) + \
"','" + str(weight_minConcealment) + "','" + str(weight_averageCover) + "','" + str(weight_averageConcealment) + \
"','" + str(weight_averageVisibleArea) + "','" + str(weight_percentBuddyTeamNotMoving) +"','" + str(weight_largestNumberBuddyTeam30Meters) + \
 "','" + str(weight_areaLeftUnsearched) + "','" + str(weight_distanceMoved) + "');"

    cursor.execute(soldier1Move)
    print("Weights added")
    connection.commit()
     
     
def getWeights():
    cursor = connection.cursor()
    cursor.execute("select percentBuddyTeamVisibleRange, minCover, minConcealment, averageCover, \
     averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, largestNumberBuddyTeam30Meters, \
areaLeftUnsearched, distance from GeneratedWeigths;")
    weights = cursor.fetchone()
    cursor.execute("delete from GeneratedWeigths where percentBuddyTeamVisibleRange =" + str(weights[0]) + ";")
    connection.commit()
    return weights
    
def getArmaRuns():
    cursor = connection.cursor()
    cursor.execute("select timestamp, opfor_remaining, bluefor_remaining, blue_sent_location_x, \
     blue_sent_location_y, percentBuddyTeamVisibleRange, minCover, minConcealment, \
      averageCover, averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, \
       largestNumberBuddyTeam30Meters, areaLeftUnsearched, distanceMoved \
        from armaruns;")
    runs = cursor.fetchall()
    return runs    
    
def getArmaRunswPandas():
    dataframe = pd.read_sql("""
           select timestamp, opfor_remaining, bluefor_remaining, blue_sent_location_x, \
     blue_sent_location_y, percentBuddyTeamVisibleRange, minCover, minConcealment, \
      averageCover, averageConcealment, averageVisibleArea, percentBuddyTeamNotMoving, \
       largestNumberBuddyTeam30Meters, areaLeftUnsearched, distanceMoved \
        from armaruns;
            """, con = credentials)
    return dataframe
    

    