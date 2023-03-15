# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 15:07:49 2023

@author: karat
"""

import math

#https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
def generateTestpoints(radius_button, numPoints):
    radius = radius_button - 0.1 #so the very edge is not pressed
    points = []
    points.append([0,0,None,None])
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
        points.append([round(curr_x, 2),round(curr_y, 2),None,None])
    return points

print(generateTestpoints(10,4))