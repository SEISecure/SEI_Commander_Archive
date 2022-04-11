import torch
import csv
import numpy
from torch import nn


# this function takes in the distance to cloesest enemy, percentage of blue force dead, percentage of blue force wounded

#def deepLearningMode(distanceClosestEnemy, percentageBlueForceDead, percentageBlueForceWounded): #all values should be floats
dtype = torch.float
device = torch.device("cpu")

D_in, H_one, H_two, H_three, D_out = 5, 5, 5, 5, 1
model = nn.Sequential(
nn.Linear(D_in, H_one),
nn.ReLU(),

nn.Dropout(0.2),
nn.Linear(H_one, H_two),
nn.ReLU(),
nn.Dropout(0.2),
nn.Linear(H_two, H_three),
nn.ReLU(),
nn.Dropout(0.2),
nn.Linear(H_three, D_out),
)
#calls the trained model and sets it for evaluation mode
model.load_state_dict(torch.load('C:/Users/Mo/My Documents/LiClipse Workspace/ConnectToVBS3/src/connnection/Model.pth'))
model.eval()
commandOrder = 1
distanceClosestEnemy = 100
percentageBlueForceDead = .2
percentageBlueForceWounded = .3
assaultMatrix =numpy.array([[1,0,distanceClosestEnemy, percentageBlueForceDead,percentageBlueForceWounded]])
fallbackMatrix =numpy.array([[0,1,distanceClosestEnemy, percentageBlueForceDead,percentageBlueForceWounded]])
flankMatrix = numpy.array([[0,0,distanceClosestEnemy, percentageBlueForceDead,percentageBlueForceWounded]])

assaultNode = torch.tensor(assaultMatrix,device=device, dtype=dtype)
fallbackNode = torch.tensor(fallbackMatrix,device=device, dtype=dtype)
flankNode = torch.tensor(flankMatrix,device=device, dtype=dtype)

assaultOutput = model(assaultNode)
assaultOutput = float(str(assaultOutput[0].item()))
#print(assaultOutput)


fallbackOutput = model(fallbackNode)
fallbackOutput = float(str(fallbackOutput[0].item()))
#print(fallbackOutput)


flankOutput = model(flankNode)
flankOutput = float(str(flankOutput[0].item()))
#print(flankOutput)

if fallbackOutput > assaultOutput and fallbackOutput > flankOutput:
    commandOrder = 2
elif  flankOutput > assaultOutput and flankOutput > fallbackOutput:
    commandOrder = 3
#return commandOrder #1 = assault, 2 = fallback, 3 = flank order troups to perform action