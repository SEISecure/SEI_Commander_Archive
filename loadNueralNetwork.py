import torch
import csv
import numpy
import io


def loadModel(modelName):
    dtype = torch.float
    device = torch.device("cpu")
    D_in, H_one, H_two,  D_out = 7, 7, 7, 2
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
    #path = 'C:/Downloads/opForceAgent/'
    
    model.load_state_dict(torch.load(modelName+'.pth'))
    
    model.eval()
    
    #out_pred = model(inputNodes)
    return  model