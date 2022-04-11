import torch
import csv
import numpy
import io
import os
import glob
import datetime
import re



#This code builds a neural network that predicts if a soldier will be alive in 10 sec
 

path = 'C:/Downloads/opForceAgent/'

dataSet =[]
for filename in glob.glob(os.path.join(path, '*.csv')):
    with open(os.path.join(os.getcwd(), filename), 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        firstLine = True
        lastLocation ={}
        temp=[]
        for lineData in csv_reader: # is a list
            if not firstLine:
                DNE = round(float(lineData[3]))
                health = float(lineData[15])
                if DNE < 300 and health <=0.99: #enemy within 300 meters and soldier is alive
                    date_time_str = lineData[0]
                    if re.search('\.', date_time_str):
                        date_time_obj = datetime.datetime.strptime(date_time_str, '%H:%M:%S.%f')
                    else:
                        date_time_obj = datetime.datetime.strptime(date_time_str, '%H:%M:%S')
                    UnitName = lineData[1]  
                    DNA = round(float(lineData[2]))
                    AllySector = lineData[4][0] 
                    numEnmSectNorth =0
                    numEnmSectEast =0
                    numEnmSectSouth =0
                    numEnmSectWest =0
                    for sect in lineData[5]:
                        if sect =='1':
                            numEnmSectNorth+=1
                        elif sect =='2':
                            numEnmSectEast+=1
                        elif sect =='3':
                            numEnmSectSouth+=1
                        elif sect =='4':
                            numEnmSectWest+=1
                    NearestEType =0
                    if lineData[6] != 'Rifleman':
                        NearestEType=1
                    GreatestAngle = round(float(lineData[7]),1) 
                    SmallestAngle = round(float(lineData[8]),1)
                    ElevationDiff = round(float(lineData[13]),1)    
                    Elevation = round(float(lineData[14]))  
                    lineData[16] = lineData[16].replace("[","")
                    lineData[16] = lineData[16].replace("]","")
                    PercentForestAtEnemy =  round(float(lineData[16]),1)
                    lineData[17] = lineData[17].replace("[","")
                    lineData[17] = lineData[17].replace("]","") 
                    PercentForestAtSol  =   round(float(lineData[17]),1)
                    PercentForestNorthSector =  round(float(lineData[18]),1)    
                    PercentForestSouthSector=   round(float(lineData[19]),1)    
                    PercentForestEastSector =   round(float(lineData[20]),1)
                    PercentForestWestSector=    round(float(lineData[21]),1)
                    temp.append([UnitName,  date_time_obj,0, DNA, DNE, numEnmSectNorth, numEnmSectEast, numEnmSectSouth, numEnmSectWest,NearestEType,GreatestAngle, SmallestAngle, ElevationDiff,Elevation, PercentForestAtEnemy, PercentForestAtSol, PercentForestNorthSector, PercentForestSouthSector, PercentForestEastSector,PercentForestWestSector])
            else:
                firstLine = False
        #checks to determine if the soldier is alive in 10 seconds
        i = 0
        for data in temp:
            currentName = data[0]
            currentTime = data[1]
            for x in range(i+1, len(temp)):
                testName = temp[x][0]
                if currentName == testName:
                    testTime = temp[x][1]
                    difference = testTime - currentTime
                    if difference.seconds > 10:
                        temp[i][2]=1
                        break
                x+=1
            i+=1
        dataSet.append(temp)
 

finaldata = []
for i in dataSet:
    for t in i:
        finaldata.append(t)
dataSet=[]




#making array for input and output variables
input =numpy.array([])
output = numpy.array([])
for data in finaldata:
    outPutVars = [data[2]]
    tempOutput = numpy.array([outPutVars])
    tempList =[]
    for i in range(3, len(data)):
        tempList.append(data[i])
    tempInput = numpy.array([tempList])
    if(len(input)==0):
        input = tempInput
        output = tempOutput
    else:
        input = numpy.append(input,tempInput, axis = 0)
        output = numpy.append(output,tempOutput, axis = 0)   

num_rows, num_cols = input.shape

dtype = torch.float
device = torch.device("cpu")
 
inputNodes = torch.tensor(input,device=device, dtype=dtype)
outputNodes = torch.tensor(output,device=device, dtype=dtype)
#fully connected graph. Two hidden layers becuase values are hidden
D_in, H_one, H_two,  D_out = 17, 17, 17, 1
model = torch.nn.Sequential(
torch.nn.Linear(D_in, H_one),
torch.nn.ReLU(),
torch.nn.Dropout(0.2),
torch.nn.Linear(H_one, H_two),
torch.nn.ReLU(),
torch.nn.Dropout(0.2),
torch.nn.Linear(H_two, D_out),
torch.nn.Sigmoid(),
)

 

loss_fn = torch.nn.MSELoss(reduction='sum')
learning_rate = 1e-4
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
t = 0
lost = 1000
done = True
model.train()
maxIteration = 100000
while  t < maxIteration and done:
    t+=1
    # Forward pass: compute predicted y by passing x to the model.
    out_pred = model(inputNodes)
    #print (out_pred[0])
 

    # Compute and print loss.
    loss = loss_fn(out_pred, outputNodes)


    if t % 1000 == 99:
        print(t, loss.item())
        #lost = abs(lost - float(loss[0]))

        diff =abs(float(str(loss.item()))-lost)
        #print(diff)
        #if diff < 0.05:
        #    done = False
        lost = float(str(loss.item()))
        #print(lost)

        

        

 

    # Before the backward pass, use the optimizer object to zero all of the
    # gradients for the variables it will update (which are the learnable
    # weights of the model). This is because by default, gradients are
    # accumulated in buffers( i.e, not overwritten) whenever .backward()
    # is called. Checkout docs of torch.autograd.backward for more details.
    optimizer.zero_grad()

 

    # Backward pass: compute gradient of the loss with respect to model
    # parameters
    loss.backward()

 

    # Calling the step function on an Optimizer makes an update to its
    # parameters
    optimizer.step()

 

#output = open('C:/Users/Roy Hayes/Documents/Current Projects/Department of Defense/Navy/ONR/Ambush Mission/Model.pth', mode="wb")

torch.save(model.state_dict(), path+'soldierModel.pth')