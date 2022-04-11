#!/usr/bin/env python3

import socket, errno, sys, struct, subprocess, re
import threading
import time
#from athena_messages import MobilityTaskRequest, Timestamp, MobilityTask, LLA_Waypoint, MobilityTaskStatus, LocalizationSolution, SquadCommand
from driver_commander_pb2 import SquadCommand
import psycopg2
import numpy as np
import argparse
import asyncio

from asyncio import DatagramProtocol
from datetime import datetime


connection = psycopg2.connect(user = "postgres",
                                  password = "ichigo",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "units")

def DBSaveDetection(TimeStamp, Uname, Tname, X, Y, Z):
    cursor = connection.cursor()
    detectionSQL = "insert into detections (timestamp, unit_name, target_name, target_x, target_y, target_z) values (TIMESTAMP '"  + str(TimeStamp) + "','" + Uname + "','" + Tname +  "','" + str(X) +  "','" + str(Y) +  "','" + str(Z) + "');"
    cursor.execute(detectionSQL)
    connection.commit()

def DBSavePositionData(TimeStamp, Uname, X, Y, Z, health, side):
    cursor = connection.cursor()
    positionDataSQL = "insert into positiondata (timestamp, unit_name,  px, py, pz, health, side) values ('"  + str(TimeStamp) + "','" + Uname + "','" + str(X) +  "','" + str(Y) +  "','" + str(Z) +  "','" + str(health) +  "','" + side + "');"
    cursor.execute(positionDataSQL)
    connection.commit()

def DBSaveTask(Command, UnitName, MoveCoord, TargetCoord):
    cursor = connection.cursor()
    cursor.execute("RollBACK")
    connection.commit()
    taskSQL = "insert into squad_command \
        (squadID, command, waypoint, unit_name, targetAreaList) \
     values ('squad1' , '" + Command + "' , '" + MoveCoord + "' , '" + UnitName + "' ,'" + TargetCoord + "' );"
    cursor.execute(taskSQL)
    connection.commit()

class AthenaReceiver(object):

    def __init__(self):
        self.athena_ip = "127.0.0.1"
        #self.athena_ip = "192.168.1.21"
        #self.athena_ip = "192.168.1.8"
        #self.athena_ip = "192.168.10.230"   #  always us receiver
        #self.athena_ip = "192.168.10.228"   #  always receiver
        self.athena_ip = "172.16.18.7"
        #self.athena_port = 3636
        self.athena_port = 4567
        messageToSend = ""
        self.set_up_connections()
        print("in init")

    def set_up_connections(self):
        try:
            """
            Socket for Receiving Protobuff to Athena.
            """
            print("1")
            self.athena_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("4")
            self.athena_socket.bind((self.athena_ip, self.athena_port));
            print("receiving from ",self.athena_ip, self.athena_port)
            self.athena_socket.settimeout(20.0);
            print("receiver set_up_connections socket set up")
        except:
            print('receiver set_up_connections error')

    def receive(self):
        #for socket_instance in self.send_sockets:
        print("IN receive")
        try:
            print("1")
            if self.athena_socket != None:
                print("1a")
                data = self.athena_socket.recv(1024)        
                print("2")
                GuiCommand = SquadCommand()  
                print("3")  
                GuiCommand.ParseFromString(data)
                print(GuiCommand)
                DBSaveTask(GuiCommand.command, GuiCommand.unit_name, GuiCommand.waypoint, GuiCommand.targetAreaList)
            else:
                print('No receiving socket')
        except:
            e0 = sys.exc_info()[0]
            e1 = sys.exc_info()[1]
            print('receive error: ', e0, e1)


class AthenaSender(object):

    def __init__(self):
        self.athena_ip = "127.0.0.1"
        #self.athena_ip = "192.168.1.21"
        #self.athena_ip = "192.168.1.8"
        self.athena_port = 3636
        messageToSend = ""
        self.set_up_connections()
        print("in init")

    def set_up_connections(self):
        try:
            """
            Socket for Sending Protobuff to Athena.
            """
            print("1")
            self.athena_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("2")
            #self.send_sockets.append([self.athena_socket, self.athena_ip, self.athena_port, "athena"])
            print("Send protobuf to Athena socket set up")
        except:
                print('protobuff socket send error')

    def send(self):
        #for socket_instance in self.send_sockets:
        print("IN send")
        try:
            self.athena_socket.connect((self.athena_ip, self.athena_port));
            print("sending to ",self.athena_ip, self.athena_port)
            # Send data to server
            data = self.messageToSend;
            self.athena_socket.send(data);
        except:
            print('set_up_connections error')



def build_message(longitude, latitude):

    # driver request message
    driver_message = MobilityTaskRequest()
    timestamp  = int(time.time())
    print(timestamp)
    driver_message.time.sec = timestamp
    driver_message.time.nsec = 0
    driver_message.request = 1  #WAYPOINT 
  
    waypoint =  LLA_Waypoint()
    waypoint.latitude = float(latitude)
    waypoint.longitude = float(longitude)
    driver_message.waypoints.extend([waypoint])
   
    print(driver_message)
    return driver_message.SerializeToString()


def getFromAthena_Asset_Command():
    cursor = connection.cursor()
    cursor.execute("select * from athena_asset_command;")
    athenaCommand = cursor.fetchall()
    #it its one row cursor.fetchone()
    return athenaCommand[0]

async def main():
    node = AthenaReceiver()
    while True:
        print("Receiving message")
        #node = AthenaReceiver()
        node.receive()

        '''
        command  = getFromAthena_Asset_Command()
        print(len(command))
        for i in range(0, len(command) - 1):
            print(i, command[i])
        print("")

        if command[1] == "move":
            print (command[1])
            values = command[2].split(",")
            for i in range(0, len(values)):
                print(i, values[i])

            longitude = values[0]
            latitude = values[1]

            print("Sending message")
            msg = build_message(longitude, latitude)
            print(msg)
            node = AthenaSender()
            node.messageToSend = msg
            node.send()
        '''
        time.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
