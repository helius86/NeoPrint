# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 16:00:40 2022
@author: karat
"""

import serial
import time
import tkinter
import math
import random #for testing
import os

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import pylab

### to plot heatmaps
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns


### constants
maxTestpoints = 500 #integer
maxRadius = 20 #in centimetres, can be float
minRatio = 0.2 #area/testpoints


def quit():
    global tkTop
    #ser.write(bytes('L', 'UTF-8'))
    tkTop.destroy()

#single test-point mode
def setToSingleMode():
        
     singleModeButton.pack_forget()
     areaModeButton.pack_forget()
     single_tp_getPoints()
     
def single_tp_getPoints():
    
     title_var.set("Single Test-point")
     print("Single test-point mode chosen")
     #ser.write(bytes('H', 'UTF-8'))
     validity.set("")

     instruction.set("\n Enter the desired test-point coordinates (x,y,z):")
     labelInstr.pack()
    
     global x_coord_tb,  y_coord_tb, z_coord_tb

     x_coord_tb = tkinter.Entry(tkTop, width=4)
     x_coord_tb.pack(pady=12)
     
     y_coord_tb = tkinter.Entry(tkTop,width=4)
     y_coord_tb.pack(pady=2)
     
     z_coord_tb = tkinter.Entry(tkTop,width=4)
     z_coord_tb.pack(pady=12)
     
     global buttonBeginSingle 
     buttonBeginSingle = tkinter.Button(tkTop, 
          text = "Begin Test", padx = 20,
          height = 2, bd = 5, bg = "green",
          command = checkValidPoint)

     if (ready.get() == 1):
         buttonBeginSingle.pack(side='top', ipadx=2, padx=2, pady=10)
     
     global buttonReturnSingle
     buttonReturnSingle = tkinter.Button(tkTop, 
          text = "Return Home", 
          height = 2, bd = 5, bg = 'red',
          command = lambda: showHome("single"))
     buttonReturnSingle.place(x=340, y=430)

def checkValidPoint():
    
     x_coord = x_coord_tb.get()
     y_coord = y_coord_tb.get()
     z_coord = z_coord_tb.get()
    
     
     # check if int and start test
     try: 
         
         #todo: add check if outside dimension of button or printer
         
        x_coord = int(x_coord)
        y_coord = int(y_coord)
        z_coord = int(z_coord)
        print("Testing started for point (x,y,z) = (" + (str)(x_coord) + "," + (str)(y_coord)  + "," + (str)(z_coord) + ")")
        validity.set("Testing started for point (x,y,z) = (" + (str)(x_coord) + "," + (str)(y_coord)  + "," + (str)(z_coord) + ")")
        valLabel.pack_forget()
        redValLabel.pack_forget()
        greenValLabel.pack(pady=10)
        
        buttonBeginSingle.pack_forget()
        #ready.set(0) #can't begin another test until previous result ready
        #to add cancel button
        
        startSingleMode(x_coord,y_coord,z_coord)
        
     except ValueError:
        print("Invalid coordinates.")
        validity.set("Invalid coordinates.")
        valLabel.pack_forget()
        greenValLabel.pack_forget()
        redValLabel.pack(pady=10)

        
     # check if float and start test 
     """ 
     if ((isNumber(x_coord)) and (isNumber(y_coord)) and (isNumber(z_coord))):
        print("(x,y,z) = (" + (str)(x_coord) + "," + (str)(y_coord)  + "," + (str)(z_coord) + ")")
        startSingleMode(x_coord,y_coord,z_coord)
        
     else:    
        print("Invalid coordinates.") 
    
     """

        
def startSingleMode(x_coord, y_coord, z_coord):
    ### to be integrated with daniel's part
    # new window pops up to show result
        # Test-point              = (x,y,z)
        # Actuation Force (gf)    = ___ 
        # Actuation Distance (mm) = ___

    singletpWindow = tkinter.Tk()
    singletpWindow.title('Results')
    singletpWindow.geometry('300x90')
    
    #dummy values for now
    force = 1
    distance = 2
    
    #ready is replacing button activation for now
    #while(ready.get() == 0):
    #    ready.set(1)
    
    button_status = 0
    
    while(button_status == "0"):
        current_data = (str(ser.readline())) #go through all data (including invalid ones)
        button_status = clean_single(current_data,2,3)
        if((button_status) == "1"):
            force = clean_single(current_data,4,9)
    
    results = tkinter.StringVar(singletpWindow)
    resultsLabel = tkinter.Label(singletpWindow, textvariable=results)
    stringToDisplay = ( "Test-point = (" + (str)(x_coord) + "," + (str)(y_coord)  + "," + (str)(z_coord) + ")" +
               "\nActuation Force (gf) = " + (str)(force) + 
               "\nActuation Distance (mm) = " + (str)(distance) )
    stringToDisplay.ljust(len(stringToDisplay))
    results.set(stringToDisplay)
    resultsLabel.pack(anchor='center',padx=5, pady=20)
    print( "Test-point = (" + (str)(x_coord) + "," + (str)(y_coord)  + "," + (str)(z_coord) + ")" +
               "\nActuation Force (gf) = " + (str)(force) + 
               "\nActuation Distance (mm) = " + (str)(distance) )
    

    
#area mode
def setToAreaMode():
    
    title_var.set("Area")
    print("Area mode chosen")
   # ser.write(bytes('L', 'UTF-8'))
    validity.set("")
    singleModeButton.pack_forget()
    areaModeButton.pack_forget()
    
    instruction.set("\n Enter the RADIUS of the button:")
    labelInstr.pack()
    
    #fetch radius of button 
    global radius
    radius = tkinter.Entry(tkTop, width=6)
    radius.pack(pady=2)
    
    global numPointsInstr
    numPointsInstr = tkinter.Label(text="\n Enter the NUMBER OF POINTS you'd like to test:")
    numPointsInstr.pack(pady=2)
    
    #fetch number of user-specified points
    global numPoints
    numPoints = tkinter.Entry(tkTop, width=6)
    numPoints.pack(pady=2)
    
    global buttonAllTestpoints
    buttonAllTestpoints = tkinter.Button(tkTop, 
         text = "See Testpoints", 
         height = 2, bd = 5, 
         command = lambda: checkValidNumPoints("generate"))
    buttonAllTestpoints.place(x=100, y=300)
        
    global buttonBeginArea
    buttonBeginArea = tkinter.Button(tkTop, 
         text = "Begin Test", 
         height = 2, bd = 5, bg = "green", padx = 20,
         command = lambda: checkValidNumPoints("begin"))
    buttonBeginArea.place(x=280, y=300)
         
    global buttonReturnArea
    buttonReturnArea = tkinter.Button(tkTop, 
         text = "Return Home", 
         height = 2, bd = 5, bg = 'red',
         command = lambda: showHome("area_before"))
    buttonReturnArea.place(x=340, y=430)
 
    
def checkValidNumPoints(button_pressed):    
    
    radiusInt = radius.get()
    numPointsInt = numPoints.get()
   
    try: 
       radiusInt = (float)(radiusInt)
       numPointsInt = (int)(numPointsInt)
       
       if (numPointsInt > 0 and numPointsInt <= maxTestpoints 
           and radiusInt > 0 and radiusInt <= maxRadius):
           
               if (button_pressed == "generate"):
                   print("Generating testpoints")
                   generateTestpoints(radiusInt, numPointsInt)
                   
               elif (button_pressed == "begin"):
                   print("Testing in progress")
                   validity.set("Testing in progress")
                   valLabel.pack(pady=10)
                   redValLabel.pack_forget()
                   greenValLabel.pack_forget()
                   radius.pack_forget()
                   numPointsInstr.pack_forget()
                   buttonReturnArea.destroy()
                   buttonAllTestpoints.destroy()
                   buttonBeginArea.destroy()
                   startAreaMode(numPointsInt, radiusInt)
                   
       else: 
           invalidNumArea()
           
    except ValueError:
        invalidNumArea()
        

def invalidNumArea():
    print("Invalid input(s)")
    validity.set("Please choose a radius within [0, " + (str)(maxRadius) + 
                 "] \n and an integer number of points within [0, " + (str)(maxTestpoints) + "]") 
    valLabel.pack_forget()
    greenValLabel.pack_forget()
    redValLabel.pack(pady=10)
    
    

#https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
def generateTestpoints(radius_button, numPoints):
    
    radius = radius_button - 0.1 #so te very edge of the button isn't pressed
    
    
    validity.set("")
    testpointsWindow = tkinter.Tk()
    testpointsWindow.title('Generated Testpoints')
    testpointsWindow.geometry('870x850')
    testpointsWindow.configure(bg = 'white')
    
    ratio = radius*radius*math.pi/numPoints
    
    
    
    fig = plt.Figure(figsize = (5.5,5.2))
    fig.tight_layout()
    testpoints_fig = fig.add_subplot(111) 

    
    #button circumference 
    circle = plt.Circle((0,0), radius, color = 'c')
    testpoints_fig.add_patch(circle)
    
    
    #testpoints
    
    # (x,y) on the plot
    points = []
    x = []
    y = []
    
    x.append(0)
    y.append(0)
    points.append([0,0,None,None]) #x, y, force, distance
    
    # https://stackoverflow.com/questions/28567166/uniformly-distribute-x-points-inside-a-circle
    # https://math.stackexchange.com/questions/227481/x-points-around-a-circle
    boundary = math.sqrt(numPoints)
    phi = (math.sqrt(5)+1)/2

    for k in range(1,numPoints):

        if (k > numPoints-boundary):
            r = radius
        else: 
            r = radius*math.sqrt(k-1/2)/math.sqrt(numPoints-(boundary+1)/2) 
       
        angle = k*2*math.pi/phi/phi 
    
        curr_x = r*math.cos(angle)
        curr_y = r*math.sin(angle)
        
        x.append(curr_x)
        y.append(curr_y)
        points.append([curr_x,curr_y,None,None])

        
    writeList2file("points.txt", points)

    colour = np.linspace(0,1,len(x))
    
    testpoints_fig.scatter(x, y, c = colour) 
    testpoints_fig.set_xlabel('x-position')
    testpoints_fig.set_ylabel('y-position')
    testpoints_fig.set_title("Testpoints Location")
    canvas = FigureCanvasTkAgg(fig, master = testpointsWindow)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    
    warning = tkinter.StringVar(testpointsWindow)
    warningLabel = tkinter.Label(testpointsWindow, textvariable=warning, bg='white', fg='red')
    if (ratio < minRatio): 
        warning.set("Warning: Too many testpoints for the area given, data might be inaccurate.")
        warningLabel.pack(anchor='center',padx=5, pady=0, )
  
    instr = tkinter.StringVar(testpointsWindow)
    instrLabel = tkinter.Label(testpointsWindow, textvariable=instr, bg='white', fg='blue')
    instr.set("The cyan circle represents the button. The dots represent the generated testpoints.\n" + 
              "Darker dots will be tested first.")
    instrLabel.pack(anchor='center',padx=5, pady=5)
        


def startAreaMode(numPointsInt, radiusInt):
    
    validity.set("")
    
    global areaPoints
    areaPoints = tkTop.counter
    
    numPointsCurr = numPointsInt
    
    while (numPointsCurr > 0):
        #send command to printer to measure at numPoints different places
        areaPoints += 1
        numPointsCurr -= 1
        #if cancelled: exit loop and use the areaPoints amount of testpoints to map force/distance if requested
   
    print(areaPoints)
    
    #after data is collected
    print("Data collection complete")
    
    labelInstr.pack_forget()
    numPoints.pack_forget()
   
    validity.set("Testing complete for " + (str)(areaPoints) + " points")
    valLabel.pack_forget()
    redValLabel.pack_forget()
    greenValLabel.pack(pady=10)
    
    all_data = []
    valid_force = []
    valid_distance = []
    valid_position = []
    count = 0
    
    global button_status
    
    #for testing
    #valid_force.append((str)(1.0000))
    #valid_force.append((str)(1.0000))
    
    
    
    while (count < numPointsInt):
        current_data = (str(ser.readline())) #go through all data (including invalid ones)
        all_data.append(current_data)
        button_status = clean_single(current_data,2,3)
        if((button_status) == "1"):
            valid_force.append(clean_single(current_data,4,9))
            #add distance, position, all other data
            #dummy data for now
            #valid_position.append((str)(count))
            count+=1
    
    
    #####################################################
    #for M3 demo (edit positions for manual testing)
    x = [(str)(1),(str)(2),(str)(13), (str)(-8)]
    y = [(str)(1),(str)(2),(str)(-13), (str)(8)]

    valid_position.append("(" + x[0] + "," + y[0] + ",1)")
    valid_position.append("(" + x[1] + "," + y[1] + ",1)")
    valid_position.append("(" + x[2] + "," + y[2] + ",1)")
    valid_position.append("(" + x[3] + "," + y[3] + ",1)")
    
    while (len(valid_position) < numPointsInt):
        valid_position.append("(0,0,0)")
        
    writeList2file("x.txt", x)
    writeList2file("y.txt", y)
    
    #####################################################
    

    #save different data types to different files 
    writeList2file("all_data.txt", all_data) #including where button is not activated
    writeList2file("position.txt", valid_position)
    writeList2file("force.txt", valid_force)
    
    count = 0
    writeWords2file("data.txt", "Position               Force(gf)", "w")
    while (count < numPointsInt):
        #readFile("force.txt")[2]#get the 2nd index (3rd line) of force
        position = (str)(valid_position[count])
        force = (str)(valid_force[count])
        writeWords2file("data.txt", position + "                      " + force, "a")
        count+=1
    
    instruction.set("Choose to display any of the following:")
    labelInstr.pack()
    
    global buttonSpreadsheet   
    buttonSpreadsheet = tkinter.Button(tkTop, 
         text = "Spreadsheet", 
         height = 2, bd = 5,
         command = displaySpreadsheet)
    buttonSpreadsheet.pack(side='top', ipadx=2, padx=2, pady=10)
    
    global buttonForceHeatmap
    buttonForceHeatmap = tkinter.Button(tkTop, 
         text = "Heatmap: Force vs. Position", 
         height = 2, bd = 5,
         command = lambda: displayForce(radiusInt))
    buttonForceHeatmap.place(x=130, y=230)

    global buttonDistHeatmap
    buttonDistHeatmap = tkinter.Button(tkTop, 
         text = "Heatmap: Distance vs. Position", 
         height = 2, bd = 5,
         command = displayDist)
    buttonDistHeatmap.pack(side='top', ipadx=2, padx=2, pady=10)
    
    global buttonReturnArea 
    buttonReturnArea = tkinter.Button(tkTop, 
         text = "Return Home", 
         height = 2, bd = 5, bg = 'red',
         command = lambda: showHome("area_after"))
    buttonReturnArea.place(x=340, y=430)
    

def displaySpreadsheet():
    os.startfile("data.txt")


#https://www.instructables.com/Sending-Data-From-Arduino-to-Python-Via-USB/
def clean(raw_list, a, b): #list
    clean_list = []
    for i in range(len(raw_list)): # count
        temp = raw_list[i][a:] 
        clean_list.append(temp[:-b]) #cut from index a to b (b-a+1 total characters)
            
    return clean_list

def clean_single(raw_data, a, b): #list
    clean_data = raw_data[a:b] #cut from index a to b (b-a+1 total characters)
    return clean_data

def writeList2file(name, data_list):
    file=open(name, mode='w')
    for i in range(len(data_list)):
        file.write(data_list[i]+'\n') #write each index to different lines
    file.close()

def readFile(name):
    file=open(name, mode='r')
    data = file.readlines()
    file.close() 
    return data #as list 

def writeWords2file(name, words, m):
    file=open(name, mode=m) #w for overwrite, a for append
    file.write(words+'\n') 
    file.close()


#https://www.geodose.com/2018/01/creating-heatmap-in-python-from-scratch.html
def displayForce(radius):
 
    #POINT DATASET
    x=clean(readFile("x.txt"),0,1)
    y=clean(readFile("y.txt"),0,1)
    force=clean(readFile("force.txt"),0,3)
    #convert to int
    x = list(map(int, x))
    y = list(map(int, y))
    force = list(map(float, force))
    force = list(map(int, force))
    
    #create an intensity heatmap by replicating (x,y) for Force amount of times
    count = 0
    curr_count = 0
    curr_len = len(x)
    while(count < curr_len):
        while(curr_count < force[count]):
            x.append(x[count])
            y.append(y[count])
            curr_count += 1
        curr_count = 0
        count+=1
    
    #DEFINE GRID SIZE AND RADIUS(h)
    grid_size=1
    h=radius
    
    #GETTING X,Y MIN AND MAX
    x_min=-radius
    x_max=radius
    y_min=-radius
    y_max=radius
    
    #CONSTRUCT GRID
    x_grid=np.arange(x_min-h,x_max+h,grid_size)
    y_grid=np.arange(y_min-h,y_max+h,grid_size)
    x_mesh,y_mesh=np.meshgrid(x_grid,y_grid)
    
    #GRID CENTER POINT
    xc=x_mesh+(grid_size/2)
    yc=y_mesh+(grid_size/2)
    
    #FUNCTION TO CALCULATE INTENSITY WITH QUARTIC KERNEL
    def kde_quartic(d,h):
        dn=d/h
        P=(15/16)*(1-dn**2)**2
        return P
    
    #PROCESSING
    intensity_list=[]
    for j in range(len(xc)):
        intensity_row=[]
        for k in range(len(xc[0])):
            kde_value_list=[]
            for i in range(len(x)):
                #CALCULATE DISTANCE
                d=math.sqrt((xc[j][k]-x[i])**2+(yc[j][k]-y[i])**2) 
                if d<=h:
                    p=kde_quartic(d,h)
                else:
                    p=0
                kde_value_list.append(p)
            #SUM ALL INTENSITY VALUE
            p_total=sum(kde_value_list)
            intensity_row.append(p_total)
        intensity_list.append(intensity_row)
    
    #HEATMAP OUTPUT    
    intensity=np.array(intensity_list)
    plt.pcolormesh(x_mesh,y_mesh,intensity)
    plt.plot(x,y,'ro')
    plt.colorbar()

    
    plt.show()
 


    


def displayDist():
    distWindow = tkinter.Tk()
    distWindow.title('Heatmap: Distance vs. Position')
    distWindow.geometry('800x800')
    # to be added
    

def showHome(lastMode):
    
    #reset printer to normal position
    
    if (lastMode == "single"):
        x_coord_tb.pack_forget()
        y_coord_tb.pack_forget()
        z_coord_tb.pack_forget()
        buttonBeginSingle.pack_forget()
        buttonReturnSingle.destroy() 
        valLabel.pack_forget()
        greenValLabel.pack_forget()
        redValLabel.pack_forget()
        
    elif (lastMode == "area_before"):
            
        numPoints.pack_forget()
        buttonAllTestpoints.destroy()
        buttonBeginArea.destroy()
        buttonReturnArea.destroy() 
        valLabel.pack_forget()
        greenValLabel.pack_forget()
        redValLabel.pack_forget()
        radius.pack_forget()
        numPointsInstr.pack_forget()
        
    elif (lastMode == "area_after"):
        
        numPoints.pack_forget()
        buttonBeginArea.destroy()
        buttonReturnArea.destroy() 
        buttonSpreadsheet.pack_forget()
        buttonForceHeatmap.destroy()
        buttonDistHeatmap.pack_forget()
        valLabel.pack_forget()
        greenValLabel.pack_forget()
        redValLabel.pack_forget()
    
    
    title_var.set("Mode Selection")
    ready.set(1)
    instruction.set("\n Please select a testing mode.")
    labelInstr.pack()
    singleModeButton.pack(side='top', ipadx=10, padx=10, pady=15)
    areaModeButton.pack(side='top', ipadx=10, padx=10, pady=15)
    #tkButtonQuit.pack(side='bottom', ipadx=10, padx=10, pady=15)
    
    tkTop.counter = 0



#ser = serial.Serial('com4', 9600) ###check to see if port is correct
ser = serial.Serial('com4', 115200)
print("Program started")
time.sleep(3)
#ser.write(bytes('L', 'UTF-8'))

tkTop = tkinter.Tk()
tkTop.geometry('500x550')
tkTop.title("Button Test")

title_var = tkinter.StringVar()
page_title = tkinter.Label(textvariable = title_var
                      ,font=("MS Sans Serif", 12,'bold'))
page_title.pack()

instruction = tkinter.StringVar()
labelInstr = tkinter.Label(textvariable=instruction)

validity = tkinter.StringVar()
valLabel = tkinter.Label(textvariable=validity, 
                         anchor='s', font=("MS Sans Serif",10,'bold'), 
                         fg = "orange")

greenValLabel = tkinter.Label(textvariable=validity, 
                          anchor='s', font=("MS Sans Serif",10,'bold'), 
                          fg = "green")

redValLabel = tkinter.Label(textvariable=validity, 
                          anchor='s', font=("MS Sans Serif",10,'bold'), 
                          fg = "red")

ready = tkinter.IntVar()



# turn on LED on Arduino to show GUI can interact with Arduino
singleModeButton = tkinter.Button(tkTop,
    text="Single\nTest-point",
    command=setToSingleMode,
    height = 4,
    fg = "black",
    width = 8,
    bd = 5,
    #activebackground='green'
)

# turn off LED on Arduino 
areaModeButton = tkinter.Button(tkTop,
    text="Area",
    command=setToAreaMode,
    height = 4,
    fg = "black",
    width = 8,
    bd = 5,
    #activebackground='red'
)

#Quit
# tkButtonQuit = tkinter.Button(
#     tkTop,
#     text="Quit",
#     command=quit,
#     height = 2,
#     fg = "white",
#     width = 8,
#     bg = 'red',
#     bd = 5
# )
# tkButtonQuit.place(x=360, y=430)
    
showHome("")
    
try:
    tkinter.mainloop()

finally: 
    ser.close()