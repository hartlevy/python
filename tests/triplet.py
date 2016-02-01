#!/usr/bin/python

import math

class pythagoreanTriplet:
    def __init__(self,num):
        self.num = num
        

def findTriplet(num):
    maxNum = math.floor(math.sqrt(num))
    reach = False
    while(maxNum**2 > num/3 and reach == False):
        a = 2
        while(a<maxNum and reach == False):
            b = 1
            while(b<a and reach == False):              
                if(calculatePyth(maxNum,a,b) == num):
                    reach = True
                    print a, b, maxNum
                    print a**2,'+',b**2,'+',maxNum**2,'=',num
                else:
                    b+=1
                    
            a+=1
        maxNum-=1   

def calculatePyth(a,b,c):
    return a**2+b**2+c**2
