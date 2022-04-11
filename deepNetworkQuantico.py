import torch
import csv
import numpy
import io
dtype = torch.float
device = torch.device("cpu")
input =numpy.array([])
output = numpy.array([])
notHeader = False

with open('C:/Users/Roy Hayes/Downloads/PositionData/CombinedData.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        testString = row[0].replace('\n','')
        testString = testString.replace(' ', '')
        if notHeader:
            if testString != '':
                tempInput = ''
                outPutVars =[float(row[0]),float(row[1]),float(row[2])]

                tempOutput = numpy.array([outPutVars]) #percentage of Soldiers that lived in the next 20 seconds
                inPutVars =[]
                for y in range(3,len(row)):
                    inPutVars.append(float(row[y]))
                tempInput =numpy.array([inPutVars]) #variables for the model
                if(len(input)==0):
                    input = tempInput
                    output = tempOutput
                else:
                    input = numpy.append(input,tempInput, axis = 0)
                    output = numpy.append(output,tempOutput, axis = 0)
        else:
            notHeader = True
            
    num_rows, num_cols = input.shape
    
    inputNodes = torch.tensor(input,device=device, dtype=dtype)
    outputNodes = torch.tensor(output,device=device, dtype=dtype)

    D_in, H_one, H_two, H_three, D_out = 69, 69, 69, 69, 3
    model = torch.nn.Sequential(
    torch.nn.Linear(D_in, H_one),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_one, H_two),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_two, H_three),
    torch.nn.Sigmoid(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_three, D_out),
    )
    loss_fn = torch.nn.MSELoss(reduction='sum')
    learning_rate = 1e-4
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
t = 0
lost = 1000
done = True
model.train()
while  t < 500000 and done:
    t+=1
    # Forward pass: compute predicted y by passing x to the model.
    out_pred = model(inputNodes)
    #print (out_pred[0].item())

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
for parm in model.parameters():
    print(parm)
torch.save(model.state_dict(), 'C:/Users/Roy Hayes/Documents/Current Projects/Department of Defense/Navy/ONR/Quantico2.pth')
    #print(input)
    #print(num_rows)
#buffer=''
#with open('C:/Users/Roy Hayes/Documents/Current Projects/Department of Defense/Navy/ONR/Ambush Mission/Model.pth', 'rb') as f:
#    buffer = io.BytesIO(f.read())
'''
print("Loading Model")
#model.load_state_dict(torch.load(buffer))
D_in, H_one, H_two, H_three, D_out = 69, 69, 69, 69, 3
model = torch.nn.Sequential(
    torch.nn.Linear(D_in, H_one),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_one, H_two),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_two, H_three),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.2),
    torch.nn.Linear(H_three, D_out),
    )
model.load_state_dict(torch.load('C:/Users/Roy Hayes/Documents/Current Projects/Department of Defense/Navy/ONR/Ambush Mission/Model.pth'))
# model = torch.nn.Sequential(
model.eval()
#print(model)
for parm in model.parameters():
    print(parm)
#out_pred = model(inputNodes)
#loss = loss_fn(out_pred, outputNodes)
#print(loss.item())
'''