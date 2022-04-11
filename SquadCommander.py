import psycopg2
import numpy as np
import datetime
import database_connect_Arma
import random
import asyncio
import math
import sys
import csv
import time
import threading

#get terrain file from a computer
class ActionSelector(object):
 

    def __init__(self):
        #set connection to local db
        database_connect_Arma.setConnection("127.0.0.1")
        self.terrain = None
        
    def getTerrainFromVC(self, host):
        database_connect_Arma.setConnection(host)
        #TODO
    
    def getUnitPos(self, unitName):
        #vc will push info to sc computer sc will then send orders
        database_connect_Arma.setConnection("127.0.0.1")
        
    
    def blockingTask(self):       
        print("TODO")
    
    def attackByFire(self):
        print("TODO")
    