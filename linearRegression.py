import csv
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import math
import ReadTerrainFile
from networkx.classes.function import neighbors


def predictLethalityAtPos(open, closed, neighbors, DToPath, ElevationChanged, trainignFile):
    path = 'C:/Users/Mo/Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/'
    trainignFileCSV = trainignFile + '_ambushTraining.csv'
    #DToPath , ElevationChanged = ReadTerrainFile.findDistanceAndElevationToPath(x,z)
    #urban, open , closed =  ReadTerrainFile.getTerrainAtLocation(x,z)
    #neighbors = ReadTerrainFile.closedNeighbors(x,z)
    dataset=pd.read_csv(path+trainignFileCSV)
    xdataset = dataset.iloc[:,1:6].values
    ydataset = dataset.iloc[:,:1].values
    poly_reg=PolynomialFeatures(degree=3)
    #print(xdataset)
    X_poly=poly_reg.fit_transform(xdataset)
    
    regressor = LinearRegression()
    regressor.fit(X_poly, ydataset)
    #regressor.predict 
    #SKlearn linearRegression
    testXdataSet = np.array([[open, closed, neighbors, DToPath, ElevationChanged ]])
    #print(testXdataSet)
    XpolyTest = poly_reg.fit_transform(testXdataSet)
    return regressor.predict(XpolyTest)






def predictLethalityFT2Pos(open, closed, neighbors, DToPath, ElevationChanged):
    path = 'C:/Users/Mo/Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/'
    trainignFileCSV = 'ambushTraining_ft2.csv'
    #DToPath , ElevationChanged = ReadTerrainFile.findDistanceAndElevationToPath(x,z)
    #urban, open , closed =  ReadTerrainFile.getTerrainAtLocation(x,z)
    #neighbors = ReadTerrainFile.closedNeighbors(x,z)
    dataset=pd.read_csv(path+trainignFileCSV)
    xdataset = dataset.iloc[:,1:6].values
    ydataset = dataset.iloc[:,:1].values
    poly_reg=PolynomialFeatures(degree=3)
    #print(xdataset)
    X_poly=poly_reg.fit_transform(xdataset)
    
    regressor = LinearRegression()
    regressor.fit(X_poly, ydataset)
    #regressor.predict 
    #SKlearn linearRegression
    testXdataSet = np.array([[open, closed, neighbors, DToPath, ElevationChanged ]])
    #print(testXdataSet)
    XpolyTest = poly_reg.fit_transform(testXdataSet)
    return regressor.predict(XpolyTest)


def predictLethalityAtPosition2(open, closed, neighbors, DToPath, ElevationChanged):
    path = 'C:/Users/Mo/Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/'
    trainignFileCSV = 'ambushTraining.csv'
    #DToPath , ElevationChanged = ReadTerrainFile.findDistanceAndElevationToPath(x,z)
    #urban, open , closed =  ReadTerrainFile.getTerrainAtLocation(x,z)
    #neighbors = ReadTerrainFile.closedNeighbors(x,z)
    dataset=pd.read_csv(path+trainignFileCSV)
    xdataset = dataset.iloc[:,1:6].values
    ydataset = dataset.iloc[:,:1].values
    poly_reg=PolynomialFeatures(degree=3)
    #print(xdataset)
    X_poly=poly_reg.fit_transform(xdataset)
    
    regressor = LinearRegression()
    regressor.fit(X_poly, ydataset)
    #regressor.predict 
    #SKlearn linearRegression
    testXdataSet = np.array([[open, closed, neighbors, DToPath, ElevationChanged ]])
    #print(testXdataSet)
    XpolyTest = poly_reg.fit_transform(testXdataSet)
    return regressor.predict(XpolyTest)
