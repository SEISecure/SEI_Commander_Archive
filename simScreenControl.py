import psycopg2
import numpy as np
import asyncio
import database_connect_Arma
import win32com.client as comclt
import time
import ctypes
#scan codes reference
#https://www.win.tue.nl/~aeb/linux/kbd/scancodes-1.html
SendInput = ctypes.windll.user32.SendInput

W = 0x11
A = 0x1E
S = 0x1F
D = 0x20
Z = 0x2C
UP = 0xC8
DOWN = 0xD0
LEFT = 0xCB
RIGHT = 0xCD
ENTER = 0x1C 
NUM6 = 0x4D

#mouse control mapping using keyboard
#mouse left -  num key 4 scan code: 0x4B
#mouse right -  num key 6 scan code: 0x4D
#mouse down -  num key 2 scan code: 0x50
#mouse up -  num key 8 scan code: 0x48
#mouse left click num key 0 scan code: 0x52
#mouse right click num key . scan code: 0x53


PUL = ctypes.POINTER(ctypes.c_ulong)

#wsh= comclt.Dispatch("WScript.Shell")
async def runner():
    global wsh
    wsh= comclt.Dispatch("WScript.Shell")
    wsh.AppActivate("VBS4") # select another application
    #hold_key('{w}', 5)# send the keys you want and hold time 
    
    #pressKey(0x11)
    #time.sleep(5)
    #releaseKey(0x11)
    #time.sleep(5)
    hold_key(W, 8)
    hold_key(NUM6, 0.5)
    hold_key(0x52, 0.5)
    hold_key(0x52, 0.5)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def pressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def releaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, 
ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def hold_key(hexKeyCode, hold_time):
    pressKey(hexKeyCode)
    time.sleep(hold_time)
    releaseKey(hexKeyCode)

async def main():
    #readTerrain()
    task = asyncio.create_task(runner())
    #global terraindDict
    #print(terraindDict)
    #print(flankPosition (xEnemy, zEnemy, xTeam, zTeam))
    await task

asyncio.run(main())