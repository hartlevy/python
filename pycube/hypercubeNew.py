#File: hypercubeNew.py

from Tkinter import *
from ScrolledText import *
from math import *
import csv

#Mode defines whether we use stereo pair (BW) or anaglyph drawing
mode=1


#Point in 4D with rotation methods
class Point(object):

    global mode
    def __init__(self,x,y,z,w):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def dist(self,point2):
        d1 = self.x - point2.x
        d2 = self.y - point2.y
        d3 = self.z - point2.z
        d4 = self.w - point2.w
        
        return sqrt(d1**2+d2**2+d3**2+d4**2)

    #3D rotation in x,y,z            
    def getRotation(self,a1,a2,a3):
        x=self.x
        y=self.y
        z=self.z

        [c1,s1] = [cos(a1),sin(a1)]
        [c2,s2] = [cos(a2),sin(a2)]
        [c3,s3] = [cos(a3),sin(a3)]
        
        x1 = c1*c2*x - s1*c3*y + c1*s2*s3*y + s3*s1*z + c1*s2*c3*z
        y1 = s1*c2*x + c1*c3*y + s1*s2*s3*y - s3*c1*z + s1*s2*c3*z
        z1 = -s2*x + s3*c2*y + c2*c3*z

        return(Point(round(x1,6),round(y1,6),round(z1,6),self.w))

    #4D rotation in x,y,w
    def getRotation4(self,a1,a2,a3):
        x=self.x
        y=self.y
        z=self.z
        w=self.w

        [c1,s1] = [cos(a1),sin(a1)]
        [c2,s2] = [cos(a2),sin(a2)]
        [c3,s3] = [cos(a3),sin(a3)]

        x1 = c1*x + s1*s2*y + s1*c2*s3*z + s1*c2*c3*w
        y1 = c2*y - s2*s3*z - s2*c3*w
        z1 = c3*z - s3*w
        w1 = -s1*x + c1*s2*y + c1*c2*s3*z + c1*c2*c3*w
        
        return(Point(round(x1,6),round(y1,6),round(z1,6),round(w1,6)))

    
    def rotate(self,a1,a2,a3):
        self=self.getRotation(a1,a2,a3)

    def rotate4(self,a1,a2,a3):
        self=self.getRotation4(a1,a2,a3)       


#Polytope- a collection of 4-D points
        #canvas - on which to draw polytope
        #scale - a scaling factor for the polytope. Useful for fitting on canvas
        #per - a perspective factor for the polytope. Effects drawing
class Polytope(object):

    def __init__(self,canvas,scale,per):

        self.scale = scale
        self._per = per
        self.canvas = canvas

        self.p = []

    @property
    def per(self):
        return self._per
    @per.setter
    def per(self,value):
        self._per = value

    #Decrease the perspective, i.e. bring closer to the viewer
    def shrinkP(self):
        self.per -= 0.1
        if self.per<0.5:
            self.per=0.5
        self.draw()

    #Rescale to fit in canvas
    def rescale(self):
        cx=0
        cy=0
        cz=0
        cw=0
        xMax=-1000
        xMin = 1000
        size = len(self.p)
        for n,point in enumerate(self.p):
            cx = cx + point.x
            cy = cy + point.y
            cz = cz + point.z
            cw = cw + point.w

            xMax = max(xMax, point.x, point.y, point.z, point.w)
            xMin = min(xMin, point.x, point.y, point.z, point.w)
            
        cx = cx/size
        cy = cy/size
        cz = cz/size
        cw = cw/size
        scale=(xMax-xMin)

        for n,point in enumerate(self.p):
            point.x = (point.x - cx)/scale
            point.y = (point.y - cy)/scale
            point.z = (point.z - cz)/scale
            point.w = (point.w - cw)/scale
            

        
    #Increase perspective, i.e. bring further from viewer
    def growP(self):
        self.per += 0.1
        if self.per>1:
            self.per=1   
        self.draw()

    #4D Rotations about axes x,y,w (or 1,2,3)
    def rot3(self,a):
        self.rotate4(0,0,a)
        self.draw()
    def rot2(self,a):
        self.rotate4(0,a,0)
        self.draw()
    def rot1(self,a):
        self.rotate4(a,0,0)
        self.draw()

    #3D rotations about axes x,y,z
    def rot3b(self,a):
        self.rotate(0,0,a)
        self.draw()
    def rot2b(self,a):
        self.rotate(0,a,0)
        self.draw()
    def rot1b(self,a):
        self.rotate(a,0,0)
        self.draw()        

    #Arbitrary 4D rotation in x,y,w space
    def rotate4(self,a1,a2,a3):
        for n,point in enumerate(self.p):
            self.p[n] = point.getRotation4(a1,a2,a3)

    #Arbitrary 3D rotation in x,y,z space
    def rotate(self,a1,a2,a3):
        for n,point in enumerate(self.p):
            self.p[n] = point.getRotation(a1,a2,a3)

    #Abstract draw        
    def draw(self):
        self.canvas.delete('all')
            

    def drawPoint(self,point,per,offset):
        [x,y] = self.getCoordinates(point,per)
        self.canvas.create_line(offset+self.scale*(1.5+x),50+self.scale*(1+y),offset+self.scale*(1.5+x)+1,50+self.scale*(1+y)) 

    def drawLine(self,point1,point2,offset,col="black"):
        per = self.per
        [x,y] = self.getCoordinates(point1,per)
        [x2,y2] = self.getCoordinates(point2,per)
        self.canvas.create_line(offset+self.scale*(1.5+x),50+self.scale*(1+y),offset+self.scale*(1.5+x2),50+self.scale*(1+y2),fill=col) 

    #Draw line between 2 points of polytope for both images of stereo pair
    def draw3DLine(self, point1, point2):
        global mode
        q1 = point1.getRotation(0,-0.15,0)
        q2 = point2.getRotation(0,-0.15,0)

        if mode==1:
            col1="red"
            col2="#0FF"
            sep1=self.scale*1.1
            sep2=self.scale*1.12
        else:
            col1=col2="black"
            sep1=0
            sep2=self.scale*2.2
        self.drawLine(point1,point2,sep1,col1)
        self.drawLine(q1,q2,sep2,col2)

    #Screen coordinates of a given point and perspective
    def getCoordinates(self,p1,per):
        x=p1.x
        y=p1.y
        z=p1.z
        w=p1.w

        perspectiveShift=round(per**w,3)
        #x1=x*per**z*per**w
        #y1=y*per**z*per**w

        x1=x*perspectiveShift
        y1=y*perspectiveShift
        return[x1,y1]

    #Draw line between points indexed at m and n
    def connect(self,m,n):
        if m < len(self.p) and n < len(self.p):
            self.draw3DLine(self.p[m],self.p[n])                   
            
    def reset(self):
        self.__init__(self.canvas,self.scale,1)
        self.draw()

#Generic polytope which can be manually built
class GenericTope(Polytope):


    def __init__(self,canvas,scale,per):
        Polytope.__init__(self,canvas,scale,per)
        self.start = []
        self.p = []


    def getEdges(self):
        l = len(self.p)
        dists = [[[0,0] for x in range(l)] for x in range(l)]
        self.edges = []
        for n,point in enumerate(self.p):
            for m in range(l):
                dists[n][m]=[m,round(point.dist(self.p[m]),3)]
            dists[n].sort(key=lambda tup: tup[1])

            for m in range(l):
                if m <= 4:
                    if ~([n,m] in self.edges):
                        self.edges.append([n,int(dists[n][m][0])])
    def draw(self):
        self.canvas.delete('all')
        l = len(self.p)

        for edge in self.edges:
            self.draw3DLine(self.p[int(edge[0])],self.p[int(edge[1])])
            
    def reset(self):
        self.p = list(self.start)
        self.rescale()
        self.getEdges()
        self.draw()                                


#4-d folded heart shape
class Heart(Polytope):
    def __init__(self,canvas,scale,per):
        Polytope.__init__(self,canvas,scale,per)

        self.p.append(Point(0,1,0,0))
        self.p.append(Point(0.36,0.65,0,0.2))
        self.p.append(Point(0.80,0.15,0,+0.3))
        self.p.append(Point(1.03,-0.45,0,0.1))
        self.p.append(Point(0.95,-0.70,0,-0.05))
        self.p.append(Point(0.75,-0.90,0,-0.2))
        self.p.append(Point(0.50,-0.95,0,-0.25))
        self.p.append(Point(0.20,-0.85,0,-0.3))
        self.p.append(Point(0,-0.6,0,0.3))
        self.p.append(Point(-0.20,-0.85,0,-0.25))
        self.p.append(Point(-0.50,-0.95,0,-0.2))
        self.p.append(Point(-0.75,-0.90,0,0))
        self.p.append(Point(-0.95,-0.70,0,0.1))
        self.p.append(Point(-1.03,-0.45,0,0.2))
        self.p.append(Point(-0.80,0.15,0,+0.35))
        self.p.append(Point(-0.36,0.65,0,-0.2))

        self.p.append(Point(-0.55,-0.45,0.25,-0.18))
        self.p.append(Point(-0.55,-0.45,-0.25,-0.18))
        self.p.append(Point(0.55,-0.45,0.25,-0.23))
        self.p.append(Point(0.55,-0.45,-0.25,-0.23))
        self.p.append(Point(0,-0.25,0.3,0.3))
        self.p.append(Point(0,-0.25,-0.3,0.3))
        self.p.append(Point(0.1,0.1,0.23,-0.6))
        self.p.append(Point(0.1,0.1,-0.23,-0.6))
        self.p.append(Point(-0.1,0.1,0.23,-0.25))
        self.p.append(Point(-0.1,0.1,-0.23,-0.25))
        self.p.append(Point(0,0.6,0.1,0))
        self.p.append(Point(0,0.6,-0.1,0))
        
        self.rot1(pi/2)
        self.rot2b(pi/2)       

    def draw(self):
        self.canvas.delete('all')

        for n in range(0,15):
            self.connect(n,n+1)                   
        self.connect(15,0)
        
        for n in range(2,8):
            self.connect(n,18)
            self.connect(n,19)
            self.connect(n+7,16)
            self.connect(n+7,17)
        for n in range(1,3):
            self.connect(n,22)
            self.connect(n,23)
            self.connect(n+6,21)
            self.connect(n+6,20)
        
        self.connect(20,16)
        self.connect(24,16)
        self.connect(21,17)
        self.connect(25,17)

        for n in range(18,26):
            self.connect(n,n+2)
            self.connect(n,n+4)
        for n in range(20,28):
            if n < 22:
                self.connect(n,7)
                self.connect(n,9)
            if n > 21:
                self.connect(n,1)
                self.connect(n,15)
            if n == 22 or n ==23:
                self.connect(n,2)
                self.connect(n+2,14)
                self.connect(n+4,0)
            

#4-D cross polytope (hyper-octohedron)
class Cross(Polytope):
    def __init__(self,canvas,scale,per):
        Polytope.__init__(self,canvas,scale,per)

        self.p.append(Point(1,0,0,0))
        self.p.append(Point(-1,0,0,0))
        self.p.append(Point(0,1,0,0))
        self.p.append(Point(0,-1,0,0))
        self.p.append(Point(0,0,1,0))
        self.p.append(Point(0,0,-1,0))
        self.p.append(Point(0,0,0,1))
        self.p.append(Point(0,0,0,-1))
        
    def draw(self):
        self.canvas.delete('all')

        for n in range(0,8):
            for m in range(0,8):
                if(m!=n and not(abs(m-n)==1 and floor(m/2.0)==floor(n/2.0))):
                    self.draw3DLine(self.p[n],self.p[m])                   

#4-simplex (pentachoron)
class Simplex(Polytope):
    def __init__(self,canvas,scale,per):

        self.scale = scale
        self._per = per
        self.canvas = canvas

        self.p = []

        self.p.append(Point(1/sqrt(2),0,-1/2.0,0))
        self.p.append(Point(-1/sqrt(2),0,-1/2.0,0))
        self.p.append(Point(0,1/sqrt(2),1/2.0,0))
        self.p.append(Point(0,-1/sqrt(2),1/2.0,0))
        self.p.append(Point(0,0,0,1))

    def draw(self):
        self.canvas.delete('all')

        for n in range(0,5):
            for m in range(0,5):
                if(m!=n):
                    self.draw3DLine(self.p[n],self.p[m])                   

#4D Cube (Tesseract)
class Cube(Polytope):
    def __init__(self,canvas,scale,per):

        self.scale = scale
        self._per = per
        self.canvas = canvas

        self.p = [] 

        for n in range(0,16):
            x = 0.5 if (n<8) else -0.5
            y = 0.5 if (n%8<4) else-0.5
            z = 0.5 if (n%4<2) else -0.5
            w = 0.5 if (n%2<1) else -0.5
            p1 = Point(x,y,z,w)
            self.p.append(p1)

    def draw(self):
        self.canvas.delete('all')
        for n in range(0,16):
            a = 1 if (n%2 == 0) else -1
            b = 2 if (n%4 < 2) else -2
            c = 4 if (n%8 < 4) else -4
            d = 8 if (n<8) else -8
            
            self.draw3DLine(self.p[n],self.p[n+a])
            self.draw3DLine(self.p[n],self.p[n+b])
            self.draw3DLine(self.p[n],self.p[n+c])
            self.draw3DLine(self.p[n],self.p[n+d])                   

class MainApp(object):    
    def __init__(self,master=None):
        self.allowPress = True
        self.pressed = False
        self.r=Tk()
        self.canvas=Canvas(self.r,width=700,height=500)
        self.canvas.configure(background="white")
        self.canvas.pack()

        #Option 1: Load polytope from file here
        points= self.readFile("test.csv")
        self.cube=GenericTope(self.canvas,120,1)
        self.cube.start = points
        self.cube.reset()

        #Option 2: use pre-defined polytope class from above
        #Try Simplex, Cube, Heart, Cross
        self.cube = Simplex(self.canvas,120,1)

        
        self.cube.draw()
        self.frame = Frame(self.r)
        self.frame.pack()
        self.reset = Button(self.frame,text="reset",command=self.cube.reset)
        self.reset.pack(side=LEFT)
        grow = Button(self.frame,text="further",command=self.cube.growP)
        grow.pack(side=LEFT)
        shrink = Button(self.frame,text="closer",command=self.cube.shrinkP)
        shrink.pack(side=RIGHT)
        self.modeButton = Button(self.frame,text="monochrome",command=self.switchMode)
        self.modeButton.pack(side=RIGHT)        


    #Read a csv input with points that can be used to build a GenericTope
    def readFile(self, filename):
        with open(filename,"r") as csvfile:
            freader = csv.reader(csvfile)
            points=[]
            for row in freader:
                if(len(row) == 4):
                    point = Point(row[0],row[1],row[2],row[3])
                    points.append(point)
                    
            return points
                
    
        
    def switchMode(self):
        global mode
        if self.modeButton["text"] == "monochrome":
            self.modeButton["text"] = "anaglyph"
            mode = 0
        else:
            self.modeButton["text"] = "monochrome"
            mode=1

        self.cube.draw()
        
    def up(self,event):
        self.pressed = True
        self.animate2(self.cube,-pi/80)

    def down(self,event):
        self.pressed = True
        self.animate2(self.cube,pi/80)
        
    def left(self,event):
        self.pressed = True
        self.animate1(self.cube,pi/80)   
        
    def right(self,event):
        self.pressed = True
        self.animate1(self.cube,-pi/80)

    def fold1(self,event):
        self.pressed = True
        self.animate3(self.cube,pi/80)

    def fold2(self,event):
        self.pressed = True
        self.animate3(self.cube,-pi/80)     

    def turn1(self,event):
        self.pressed = True
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    self.cube.rot2b(pi/80)
                    self.cube.draw()
                    self.canvas.update()
                else:
                    break
    def turn2(self,event):
        self.pressed = True
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    self.cube.rot2b(-pi/80)
                    self.cube.draw()
                    self.canvas.update()
                else:
                    break

    def flip1(self,event):
        self.pressed = True
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    self.cube.rot3b(-pi/80)
                    self.cube.draw()
                    self.canvas.update()
                else:
                    break
    def flip2(self,event):
        self.pressed = True
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    self.cube.rot3b(pi/80)
                    self.cube.draw()
                    self.canvas.update()
                else:
                    break
                
    def curl1(self,event):
        self.pressed = True
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    self.cube.rot1b(-pi/80)
                    self.cube.draw()
                    self.canvas.update()
                else:
                    break
    def curl2(self,event):
        self.pressed = True
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    self.cube.rot1b(pi/80)
                    self.cube.draw()
                    self.canvas.update()
                else:
                    break
                
    def stopper(self,event):
        self.pressed = False
        self.allowPress = True

    def animate3(self,obj,a):
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    obj.rot3(a)
                    obj.draw()
                    obj.canvas.update()
                else:
                    break

    def animate2(self,obj,a):
        if(self.allowPress):
            self.allowPress = False
            while(True):
                if(self.pressed==True):
                    obj.rot2(a)
                    obj.draw()
                    obj.canvas.update()
                else:
                    break

    def animate1(self,obj,a):
        if(self.allowPress):
            self.allowPress = False            
            while(True):
                if(self.pressed==True):
                    obj.rot1(a)
                    obj.draw()
                    obj.canvas.update()
                else:
                    break

        

def main():
    m=MainApp()

    m.r.bind_all('<Any-KeyRelease>',m.stopper)
    m.r.bind_all('<Up>', m.flip1)
    m.r.bind_all('<Down>', m.flip2)
    m.r.bind_all('<Left>', m.turn1)
    m.r.bind_all('<Right>', m.turn2)
    m.r.bind_all('<Shift-Up>', m.up)
    m.r.bind_all('<Shift-Down>', m.down)
    m.r.bind_all('<Shift-Left>', m.left)
    m.r.bind_all('<Shift-Right>', m.right)
    m.r.bind_all('<Control-Up>', m.fold1)
    m.r.bind_all('<Control-Down>', m.fold2)
    m.r.bind_all('<Control-Left>', m.curl1)
    m.r.bind_all('<Control-Right>', m.curl2)     
    
    m.r.mainloop()

if __name__=='__main__':
    main()
