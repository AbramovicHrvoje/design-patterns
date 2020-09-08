## Hrvoje Abramovic 0036506160
## OOUP lab 4
import math
from tkinter import *


HEIGHT = 700
WIDTH = 700

class Point:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    
    def translate(self, dp):
        return Point(self.x+dp.getX(), self.y+dp.getY())
    
    def difference(self, p):
        return Point(self.x-p.getX(), self.y-p.getY())
    
    
class Rectangle:
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height
    
    def unpack(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    
class GeometryUtil:
    
    DIRECTION_NAMES = ["Left", "Up", "Right", "Down"]
    DIRECTIONS = [Point(-1, 0), Point(0, -1), Point(1, 0), Point(0, 1)]
    
    @staticmethod
    def distanceFromPoint(point1, point2):
        return math.sqrt((point1.getX()-point2.getX())**2 + (point1.getY()-point2.getY())**2)
    
    @staticmethod
    def distanceFromLineSegment(s, e, p):
        #if p.getX() < s.getX():
        #    return GeometryUtil.distanceFromPoint(s.getX(), p.getX())
        #if p.getX() > e.getX():
        SE = GeometryUtil.distanceFromPoint(s,e)
        PS = GeometryUtil.distanceFromPoint(p,s)
        PE = GeometryUtil.distanceFromPoint(p,e)
        
        h = max(PS, PE)
        k = min(PS, PE)
        result = 100
        
        if h**2 > (k**2 + SE**2):
            result =  k
        
        else:
        
            kLine = (e.getY() - s.getY())/(e.getX()-s.getX())
            kPerp = -1/kLine
            bLine = -kLine*s.getX() + s.getY()
            bPerp = -kPerp*p.getX() + p.getY()
            
            xInter = (-bLine+bPerp)/(kLine-kPerp)
            yInter = xInter*kLine + bLine
            
            intersection = Point(xInter, yInter)
            result = GeometryUtil.distanceFromPoint(intersection, p)
            
        
        return result


    def pointInsideRect(p, r):
        px = p.getX()
        py = p.getY()
        
        (rx1, ry1, rx2, ry2) = r.unpack()
        
        if px < rx1 or py < ry1:
            return False
        
        if px > rx2 or py > ry2:
            return False
        
        return True
    

class AbstractGraphicalObject:
    
    def __init__(self, hotPoints):
        self.hotPoints = hotPoints
        self.hotPointSelected = [False for h in self.hotPoints]
        self.selected  = False
        self.listeners = [] 
        return
    
    
    def getNumberOfHotPoints(self):
        return len(self.hotPoints)
    
    def getHotPoint(self, index):
        return self.hotPoints[index]
    
    def setHotPoint(self, index, point):
        self.hotPoints[index] = point
        self.notifyListeners()
        return
    
    
    def getHotPoints(self):
        return self.hotPoints.copy()
        
    def getHotPointDistance(self, index, mousePoint):
        return GeometryUtil.distanceFromPoint(self.hotPoints[index], mousePoint)
    
    def isHotPointSelected(self, index):
        return self.hotPointSelected[index]
    
    def setHotPointSelected(self, index, selected):
        self.hotPointSelected[index] = selected
        return
    
    def isSelected(self):
        return self.selected
    
    def setSelected(self, selected):
        self.selected = selected
        self.notifySelectionListeners()
        return
    
    def translate(self, delta):
        for i in range(len(self.hotPoints)):
            self.hotPoints[i] = self.hotPoints[i].translate(delta)
        
        self.notifyListeners()
        return
        
    def notifyListeners(self):
        for l in self.listeners:
            l.graphicalObjectChanged(self)
        return
    
    def notifySelectionListeners(self):
        for l in self.listeners:
            l.graphicalObjectSelectionChanged(self)
        return 
    
    
    def addListener(self, obj):
        self.listeners.append(obj)
        return
    
    def removeListener(self, obj):
        self.listeners.remove(obj)
        return
    
    def getBoundingBox(self):
        pass
    
    def selectionDistance(self, mousePoint):
        pass
    
    def getName(self):
        pass


class LineSegment(AbstractGraphicalObject):
    def __init__(self, p1 = Point(0,0), p2 = Point(15,15)):
        super().__init__([p1,p2])
    
    
    def getShapeID(self):
        return "@LINE"
    
    def save(self, rows):
        textLine = self.getShapeID() + " "
        textLine+= str(self.getHotPoint(0).getX()) + " "
        textLine+= str(self.getHotPoint(0).getY()) + " "
        textLine+= str(self.getHotPoint(1).getX()) + " "
        textLine+= str(self.getHotPoint(1).getY())
        rows.append(textLine)
        
    
    def getBoundingBox(self):
        x = self.getHotPoint(0).getX()
        y = self.getHotPoint(0).getY()
        width = self.getHotPoint(1).getX() - x
        height = self.getHotPoint(1).getY()-y
        return Rectangle(x,y,width, height)
    
    def selectionDistance(self, mousePoint):
        #return 20
        return GeometryUtil.distanceFromLineSegment(self.getHotPoint(0), self.getHotPoint(1), mousePoint)
        
    def duplicate(self):
        return LineSegment(self.getHotPoint(0), self.getHotPoint(1))
    
    def getShapeName(self):
        return "Linija"
    
    def render(self, renderer):
        s  = self.getHotPoint(0)
        e = self.getHotPoint(1)
        renderer.drawLine(s, e)
    
    
class Oval(AbstractGraphicalObject):
    def __init__(self, p1 = Point(10, 0), p2 = Point(0, 10)):
        super().__init__([p1, p2])
        #self.center = Point(p2.getX(), p1.getY())
        #self.radius = self.center.difference(p1)
        return
    
    def getBoundingBox(self):
        width = 2*(self.getHotPoint(0).getX() - self.getHotPoint(1).getX())
        height = 2*(self.getHotPoint(1).getY() - self.getHotPoint(0).getY())
        x = self.getHotPoint(1).getX() - width/2
        y = self.getHotPoint(0).getY() - height/2
        return Rectangle(x,y, width, height)

    def getShapeName(self):
        return "Oval"
    
    def getShapeID(self):
        return "@OVAL"
    
    def save(self, rows):
        textLine = self.getShapeID() + " "
        textLine+= str(self.getHotPoint(0).getX()) + " "
        textLine+= str(self.getHotPoint(0).getY()) + " "
        textLine+= str(self.getHotPoint(1).getX()) + " "
        textLine+= str(self.getHotPoint(1).getY())
        rows.append(textLine)
    
    def duplicate(self):
        return Oval(self.getHotPoint(0), self.getHotPoint(1))
    
    def selectionDistance(self, mousePoint):
        box = self.getBoundingBox()
        if GeometryUtil.pointInsideRect(mousePoint, box):
            return 0
        else:
            return 1000
        #return GeometryUtil.distanceFromPoint(self.getCenter(), mousePoint) - maxAxis
    
    def getCenter(self):
        return Point(self.getHotPoint(1).getX(), self.getHotPoint(0).getY())
    
    
    def render(self, renderer):
        ovalRect = self.getBoundingBox()
        (x1,y1,x2,y2) = ovalRect.unpack()
        renderer.drawOval(Point(x1,y1), Point(x2,y2))
      
        
class Triangle(AbstractGraphicalObject):
    def __init__(self, p1 = Point(0, 0), p2 = Point(0, 10), p3 = Point(10, 10)):
        super().__init__([p1, p2, p3])


    def getBoundingBox(self):
        x = self.getHotPoint(0).x
        y = self.getHotPoint(0).y
        
        width = self.getHotPoint(2).x - x
        height = self.getHotPoint(2).y - y
        
        return Rectangle(x,y,width,height)
    
    
    def getShapeID(self):
        return "@TRIANGLE"
    
        
    def save(self, rows):
        textLine = self.getShapeID() + " "
        textLine+= str(self.getHotPoint(0).getX()) + " "
        textLine+= str(self.getHotPoint(0).getY()) + " "
        textLine+= str(self.getHotPoint(1).getX()) + " "
        textLine+= str(self.getHotPoint(1).getY()) + " "
        textLine+= str(self.getHotPoint(2).getX()) + " "
        textLine+= str(self.getHotPoint(2).getY())
        rows.append(textLine)
        
        
    def duplicate(self):
        return Triangle(self.getHotPoint(0), self.getHotPoint(1), self.getHotPoint(2))
    
    
    def selectionDistance(self, mousePoint):
        box = self.getBoundingBox()
        if GeometryUtil.pointInsideRect(mousePoint, box):
            return 0
        else:
            return 1000
        
    def getCenter(self):
        return Point(self.getHotPoint(1).getX(), self.getHotPoint(0).getY())
    
    def render(self, renderer):
        ovalRect = self.getBoundingBox()
        (x1,y1,x2,y2) = ovalRect.unpack()
        renderer.drawLine(self.getHotPoint(0), self.getHotPoint(1))
        renderer.drawLine(self.getHotPoint(1), self.getHotPoint(2))
        renderer.drawLine(self.getHotPoint(2), self.getHotPoint(0))
    
        
        
class CompositeShape(AbstractGraphicalObject):
    def __init__(self, objects):
        self.objects = objects
        self.hotPoints = []
        
        for o in self.objects:
            self.hotPoints += o.getHotPoints()
        super().__init__(self.hotPoints)
        
        return
    
    def getShapeID(self):
        return "@COMP"
    
    
    def save(self, rows):
        
        for o in self.objects:
            o.save(rows)
            
        textLine = self.getShapeID() + " " + str(len(self.objects)) 
        rows.append(textLine)
    
    def getBoundingBox(self):
        xmin = 10000
        ymin = 10000
        xmax = -10000
        ymax = -10000
        
        for o in self.objects:
            tempBox = o.getBoundingBox()
            (x1,y1, x2, y2) = tempBox.unpack()
            
            if x1 < xmin:
                xmin = x1
            if y1 < ymin:
                ymin = y1
            if x2 > xmax:
                xmax = x2
            if y2 > ymax:
                ymax = y2
                
        return Rectangle(xmin, ymin, xmax-xmin, ymax-ymin)
    
    
    def getShapeName(self):
        return "Kompozit"
            
            
    
    def render(self, renderer):
        for o in self.objects:
            o.render(renderer)
    
        
    def selectionDistance(self, mousePoint):
        minDist = 1000000
        for o in self.objects:
            tempDist = o.selectionDistance(mousePoint)
            if tempDist < minDist:
                minDist = tempDist
                
        return minDist
    
    def translate(self, delta):
        for o in self.objects:
            o.translate(delta)
        self.notifyListeners()    
        return
    
    def getObjects(self):
        return self.objects
    

class DocumentModel:
    SELECTION_PROXIMITY  = 10
    
    def __init__(self):
        self.objects = []
        self.listeners = []
        self.selectedObjects = []
        return


    def addGraphicalObject(self, obj):
        self.objects.append(obj)
        obj.addListener(self)
        self.notifyListeners()
        
        
    def removeGraphicalObject(self, obj):
        self.objects.remove(obj)
        obj.setSelected(False)
        obj.removeListener(self)
        self.notifyListeners()
        return
    
    def notifyListeners(self):
        for l in self.listeners:
            l.documentChange()
            
        return 
    
    def getList(self):
        return self.objects.copy() 
    
    def getSelectedObjects(self):
        return self.selectedObjects.copy()
    
    def getSelectedObjectsNum(self):
        return len(self.selectedObjects)
    
    def deselectAll(self):
        for o in self.selectedObjects:
            o.setSelected(False)
        del[self.selectedObjects]
        self.selectedObjects = []
        self.notifyListeners()
    
    
    def clear(self):
        
        for o in self.objects:
            o.removeListener(self)
        
        del[self.objects]
        self.objects = []
        self.notifyListeners()
        return
    
    def addDocumentModelListener(self, l):
        self.listeners.append(l)
        return
    
    def removeDocumentModelListener(self, l):
        self.listeners.remove(l)
        return
    
    
    def increaseZ(self, go):
        index = self.objects.index(go)
        if index >= len(self.objects)-1:
            return
        
        self.objects[index+1], self.objects[index] = self.objects[index], self.objects[index+1]
        self.notifyListeners()
        return
        
        
    def decreaseZ(self, go):
        index = self.objects.index(go)
        if index <= 0:
            return
        
        self.objects[index-1], self.objects[index] = self.objects[index], self.objects[index-1]
        self.notifyListeners()
        return
    
    
    def findSelectedGraphicalObject(self, mousePoint):
        minDist = DocumentModel.SELECTION_PROXIMITY
        nearestObj = None
        
        for o in self.objects:
            tempDist = o.selectionDistance(mousePoint)
            if tempDist < minDist:
                minDist = tempDist
                nearestObj = o
            
        return nearestObj
    
    def findSelectedHotPoint(self, obj, mousePoint):
        
        minDist = DocumentModel.SELECTION_PROXIMITY
        nearestPoint = None
        nearestPointIndex = None
        
        for i in range(obj.getNumberOfHotPoints()):
            tempPoint = obj.getHotPoint(i)
            tempDist = GeometryUtil.distanceFromPoint(tempPoint, mousePoint)
            if tempDist < minDist:
               minDist = tempDist
               nearestPoint = tempPoint
               nearestPointIndex = i

        return nearestPointIndex
    
    def graphicalObjectSelectionChanged(self, obj):
        
        if obj.isSelected() and obj not in self.selectedObjects:
            self.selectedObjects.append(obj)
        
        if not obj.isSelected() and obj in self.selectedObjects:
            self.selectedObjects.remove(obj)
        
        self.notifyListeners()
        return
    
    def graphicalObjectChanged(self, obj):
        self.notifyListeners()
        return
    
    def render(self, renderer):
        for o in self.objects:
            o.render(renderer)
            
        return
    
    def outputForSave(self, rows):
        for o in self.objects:
            o.save(rows)
        return
    
    
class DocumentCanvas(Canvas):
    
    def __init__(self, root, model, state):
        self.root = root
        self.model = model
        self.state = state
        super().__init__(self.root, height = 1000)
        self.model.addDocumentModelListener(self)
        #self.root.bind('<Button-1>', self.state.mouseDown)
        self.state.addObserver(self)
        #self.config(height = 1000)
        
    def drawObjects(self):
        self.delete("all")
        
        #for o in self.model.getList():
        #    o.render(self)
            
        self.model.render(self)
        
        selected = self.model.getSelectedObjects()
        for o in self.model.getSelectedObjects():
            (x1,y1,x2,y2) = o.getBoundingBox().unpack()
            self.create_rectangle(x1,y1,x2,y2, fill = "", outline = "blue")
            
        if len(selected) == 1:
            o = selected[0]
            if o.getShapeName() == 'Kompozit':
                return
            wh = DocumentModel.SELECTION_PROXIMITY
            for hotPoint in o.getHotPoints():
                x = hotPoint.getX() - wh/2
                y = hotPoint.getY() - wh/2
                self.create_rectangle(x,y, x + wh, y+wh, fill = "", outline = "blue")
        return
  
    
    def documentChange(self):
        self.drawObjects()
        
    def drawLine(self, s, e):
        x1 = s.getX()
        y1 = s.getY()
        x2 = e.getX()
        y2 = e.getY()
        self.create_line(x1, y1, x2, y2, fill = 'blue', width = 1)
        
    def drawOval(self, p1, p2):
        self.create_oval(p1.getX(), p1.getY(), p2.getX(), p2.getY(), fill = "blue", outline = "red" )
        
    def drawPoint(self, point):
        self.create_oval(point.getX(), point.getY(), point.getX(), point.getY(), fill = "blue")
    
    
def emptyFun():
    return

def askFileName():
    return input("Unesite put i ime datoteke: ")
    

def SVGexport(documentModel):
    fileName = askFileName()
    
    svgRenderer = SVGRenderer(fileName)
    
    documentModel.render(svgRenderer)
    svgRenderer.close()
    return

def saveFile(documentModel):
    fileName = askFileName()
    
    rows = []
    
    documentModel.outputForSave(rows)
    
    with open(fileName, 'w') as outputFile:
        for r in rows:
            outputFile.write(r+"\n")
            
    return

def loadFile(documentModel):
    fileName = askFileName()
    
    documentModel.clear()
    
    objectIDs = {"@LINE":LineSegment, "@OVAL": Oval, "@COMP": CompositeShape}
    
    
    with open(fileName, 'r') as inputFile:
        lines = inputFile.readlines()
        objects = []
        
        for line in lines:
            line = line.split()
            if line[0] != "@COMP":
                points = []
                for i in range(1, len(line), 2):
                    points.append(Point(int(line[i]), int(line[i+1])))
                
                newObject = objectIDs[line[0]](points[0], points[1])
                objects.append(newObject)
            else:
                nObj = int(line[1])
                
                newObject = CompositeShape(objects[-nObj:])
            
                objects = objects[:-nObj]
                objects.append(newObject)
                
    for obj in objects:
        documentModel.addGraphicalObject(obj)
        
    documentModel.notifyListeners()
            
    return
    

class DocumentToolbar(Frame):
    def __init__(self, root, state, documentModel):
        self.root = root
        self.state = state
        self.documentModel = documentModel
        super().__init__(root, bd = 2, relief = FLAT)
        
        ## load save export line oval select delete
        self.loadButton = Button(self, text = "Ucitaj", relief = FLAT, command = lambda: loadFile(self.documentModel))
        self.loadButton.pack(side = LEFT, padx = 4)
        
        self.saveButton = Button(self, text = "Spremi", relief = FLAT, command = lambda: saveFile(self.documentModel))
        self.saveButton.pack(side = LEFT, padx = 4)
        
        self.exportButton = Button(self, text = "SVG export", relief = FLAT, command = lambda: SVGexport(self.documentModel))
        self.exportButton.pack(side = LEFT, padx = 4)
        
        self.lineButton = Button(self, text = "Linija", relief = FLAT, command =lambda: state.jumpToAddShape('Linija'))
        self.lineButton.pack(side = LEFT, padx = 4)
    
        self.ovalButton = Button(self, text = "Oval", relief = FLAT, command = lambda: state.jumpToAddShape('Oval'))
        self.ovalButton.pack(side = LEFT, padx = 4)
        
        
        self.ovalButton = Button(self, text = "Trokut", relief = FLAT, command = lambda: state.jumpToAddShape('Trokut'))
        self.ovalButton.pack(side = LEFT, padx = 4)
    
        self.selectButton = Button(self, text = "Selektiraj", relief = FLAT, command = self.state.jumpToSelect)
        self.selectButton.pack(side = LEFT, padx = 4)
    
        self.deleteButton = Button(self, text = "Brisalo", relief = FLAT, command = self.state.jumpToDeleteState)
        self.deleteButton.pack(side = LEFT, padx = 4)
        


def bindButtons(root, obj):
    root.bind('<Button-1>', obj.mouseDown)
    root.bind('<Key>', obj.keyPressed)
    root.bind('<KeyRelease>', obj.keyUp)
    root.bind('<ButtonRelease-1>', obj.mouseUp)
    root.bind('<B1-Motion>', obj.mouseDragged)


def checkValidPoint(p):
    if p.getX() <= 0 or p.getY() <= 20:
        return False
    
    return True


class State:
    
    #documentModel = None
    
    def __init__(self, documentModelArg, root):
        self.documentModel = documentModelArg
        self.root = root
        self.observers = []
        #self.multipleSelect = False
        
    def addObserver(self, obs):
        self.observers.append(obs)
        

    def notifyDrawPoint(self, point):
        for o in self.observers:
            o.drawPoint(point)
            
    def notifyEndLine(self):
        for o in self.observers:
            o.drawObjects()


    
    def jumpToSelect(self):
        self.__class__ = SelectState
        bindButtons(self.root, self)
        self.multipleSelect = False
        self.dragHotPoint = False
        self.selectedHotPoint = None
        self.hotPointObj = None
        #print(self.__class__)
        
    def jumpToIdle(self, event = None):
        #print("TU SAN")
        self.__class__ = IdleState
        bindButtons(self.root, self)
        self.documentModel.deselectAll()
        #print(self.__class__)
        
    def jumpToAddShape(self, shape):
        self.__class__ = AddShapeState
        bindButtons(self.root, self)
        self.shape = shape
        self.prototype = None
        if self.shape == 'Linija':
            self.prototype = LineSegment()
        if self.shape == 'Oval':
            self.prototype = Oval()
        if self.shape == 'Trokut':
            print("TU SAM")
            self.prototype = Triangle()
        self.documentModel.deselectAll()
        
    def jumpToDeleteState(self):
        self.__class__ = DeleteState
        bindButtons(self.root, self)
        self.documentModel.deselectAll()

        
        
        
class IdleState(State):
    def mouseDown(self, event):
        pass
    def mouseUp(self, event):
        pass
    
    def mouseDragged(self, event):
        pass
    
    def keyPressed(self, event):
        pass
    
    def keyUp(self, event):
        pass
    
        
class SelectState(State):

    #def __init__(self, documentModel):
    #    super.__init__(documentModel)
    
    def mouseDown(self, event):
        mousePoint = Point(event.x, event.y)
        if not checkValidPoint(mousePoint):
            return
        obj = self.documentModel.findSelectedGraphicalObject(mousePoint)
        if obj is not None:
            #print(obj.getShapeName())
            
            if self.documentModel.getSelectedObjectsNum() == 1 and obj == self.documentModel.getSelectedObjects()[0] and obj.getShapeName() != "Kompozit":
                ##hot point
                hotPoint = self.documentModel.findSelectedHotPoint(obj, mousePoint)
                if hotPoint is not None:
                    self.dragHotPoint = True
                    self.selectedHotPoint = hotPoint
                    self.hotPointObj = obj
                    #print("HOT POINT SELECTED")
                
            
            if not self.multipleSelect:
                self.documentModel.deselectAll()
                
            obj.setSelected(True)
        
        
    def mouseUp(self, event):
        if self.dragHotPoint:
            self.dragHotPoint = False
        pass
    
    def mouseDragged(self, event):
        if self.dragHotPoint:
            self.hotPointObj.setHotPoint(self.selectedHotPoint, Point(event.x, event.y))
        pass

    def keyPressed(self, event):
        
        if event.keysym == 'plus':
            for o in self.documentModel.getSelectedObjects():
                self.documentModel.increaseZ(o)
                
        elif event.keysym == 'minus':
            for o in self.documentModel.getSelectedObjects():
                self.documentModel.decreaseZ(o)
                
        elif event.keysym == 'Control_L' or event.keysym == 'Control_R':
            self.multipleSelect = True
            
        elif event.keysym == 'Delete':
            
            for o in self.documentModel.getSelectedObjects():
                self.documentModel.removeGraphicalObject(o)

        elif event.keysym in GeometryUtil.DIRECTION_NAMES:
            directionDelta = GeometryUtil.DIRECTIONS[GeometryUtil.DIRECTION_NAMES.index(event.keysym)]
            for o in self.documentModel.getSelectedObjects():
                o.translate(directionDelta)
                
            
        elif (event.keysym == 'g' or event.keysym == 'G') and self.documentModel.getSelectedObjectsNum() > 1:
            selectedObjs = self.documentModel.getSelectedObjects()
            newComposite = CompositeShape(selectedObjs)
            self.documentModel.addGraphicalObject(newComposite)
            for obj in selectedObjs:
                self.documentModel.removeGraphicalObject(obj)
            newComposite.setSelected(True)
            
        elif (event.keysym == 'u' or event.keysym == 'U') and self.documentModel.getSelectedObjectsNum() == 1:
            comp = self.documentModel.getSelectedObjects()[0]
            if comp.getShapeName() == 'Kompozit':
                ## DECOMPOSE COMPOSITE
                for singleObj in comp.getObjects():
                    self.documentModel.addGraphicalObject(singleObj)
                    singleObj.setSelected(True)
                    
                self.documentModel.removeGraphicalObject(comp)
                    
                
        #print(event.keysym)
        
    def keyUp(self, event):
        
        if event.keysym == 'Control_L' or event.keysym == 'Control_R':
            self.multipleSelect = False


class AddShapeState(State):
    def mouseDown(self, event):
        #print("X: " + str(event.x) + " Y" + str(event.y))
        mousePoint = Point(event.x, event.y)
        if not checkValidPoint(mousePoint):
            return
        obj = self.prototype.duplicate()
        obj.translate(Point(event.x, event.y))
        self.documentModel.addGraphicalObject(obj)
        pass
    def mouseUp(self, event):
        pass
    
    def mouseDragged(self, event):
        pass
    
    def keyPressed(self, event):
        pass
    
    def keyUp(self, event):
        pass
    
class DeleteState(State):
    

        
        
    def mouseDown(self, event):
        self.objectsToDelete = []
        
        mousePoint = Point(event.x, event.y)
        obj = self.documentModel.findSelectedGraphicalObject(mousePoint)
        if obj is not None:
            #self.documentModel.removeGraphicalObject(obj)
            self.objectsToDelete.append(obj)
        
        
    
    def mouseUp(self, event):
        
        for obj in self.objectsToDelete:
            self.documentModel.removeGraphicalObject(obj)
        
        del[self.objectsToDelete] 
        
        self.objectsToDelete = []
        self.notifyEndLine()
        pass
    
    def mouseDragged(self, event):
        mousePoint = Point(event.x, event.y)
        obj = self.documentModel.findSelectedGraphicalObject(mousePoint)
        if obj is not None and obj not in self.objectsToDelete:
            #self.documentModel.removeGraphicalObject(obj)
            self.objectsToDelete.append(obj)
        self.notifyDrawPoint(mousePoint)
    
    def keyPressed(self, event):
        pass
    
    def keyUp(self, event):
        pass
    


class SVGRenderer:
    
    def __init__(self, fileName):
        self.fileName = fileName
        self.lines = []
        
    def drawLine(self, s, e):
        #self.create_line(x1, y1, x2, y2, fill = 'blue', width = 1)
        lineText = "<line "
        lineText += '''x1="''' + str(s.getX()) + '''" '''
        lineText += '''y1="''' + str(s.getY()) + '''" '''
        lineText += '''x2="''' + str(e.getX()) + '''" '''
        lineText += '''y2="''' + str(e.getY()) + '''" '''
        lineText += '''style="stroke:rgb(0,0,255);"/>'''
        self.lines.append(lineText)
        return
        
    def drawOval(self, p1, p2):
        cx = round((p2.getX()+p1.getX())/2)
        cy = round((p2.getY()+p1.getY())/2)
        rx = round((p2.getX()-p1.getX())/2)
        ry = round((p2.getY()-p1.getY())/2)
        #self.create_oval(p1.getX(), p1.getY(), p2.getX(), p2.getY(), fill = "blue", outline = "red" )
        lineText = "<ellipse "
        lineText += '''cx="''' + str(cx) + '''" '''
        lineText += '''cy="''' + str(cy) + '''" ''' 
        lineText += '''rx="''' + str(rx) + '''" ''' 
        lineText += '''ry="''' + str(ry) + '''" '''
        lineText += '''style="fill:blue;stroke:red;"/>'''
        self.lines.append(lineText)
        return
    
    def close(self):
        with open(self.fileName, 'w') as outputFile:
            outputFile.write('''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n''')
            for line in self.lines:
                outputFile.write(line+"\n")
            outputFile.write("</svg>")
    


def main():
    
    root = Tk()
    root.title("PAINT")
    root.geometry(str(WIDTH)+"x"+str(HEIGHT))
    
    ## UBACITI MICANJE CIJELIH OBJEKATA
    ## UBACITI SAVE

    

    
    documentModel = DocumentModel()
    #l1 = LineSegment(Point(10,10), Point(700,30))
    #l2 = LineSegment(Point(150,20), Point(300,30))
    #1 = Oval(Point(500,200), Point(450,250))
    #o2 = Oval(Point(550, 220), Point(470,270))
    #documentModel.addGraphicalObject(l1)
    #documentModel.addGraphicalObject(l2)
    #documentModel.addGraphicalObject(LineSegment())
    #documentModel.addGraphicalObject(o1)
    #documentModel.addGraphicalObject(o2)
    #l1.setSelected(True)
    #o1.setSelected(False)
    #documentModel.addGraphicalObject(LineSegment(Point(0,0), Point(30,30)))
    #documentModel.addGraphicalObject(LineSegment(Point(150,20), Point(300,30)))
    #documentModel.addGraphicalObject(Oval(Point(300,100), Point(150,200)))
    State.documentModel = documentModel
    State.root = root
    state = State(documentModel, root)
    state.jumpToIdle()
    root.bind('<Escape>', state.jumpToIdle)
    canvas = DocumentCanvas(root, documentModel, state)

    
    
    toolbar = DocumentToolbar(root, state, documentModel)
        
    toolbar.pack(side = TOP, fill = X)
    canvas.pack(side = TOP, fill = BOTH, expand = YES)
    canvas.drawObjects()
    #p1 = Point(0,0)
    #p2 = Point(1,1)
    #print(GeometryUtil.distanceFromPoint(p1,p2))
    
    root.mainloop()
    
    return


main()