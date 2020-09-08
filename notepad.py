# Hrvoje Abramovic 0036506160
# OOUP, 3. lab, zadatak 2
from tkinter import *
from tkinter import font
import os
import importlib
import sys




class Location:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        
    def copy(self):
        return Location(self.row, self.column)
        
class LocationRange:
    def __init__(self, loc1, loc2):
        self.loc1 = loc1
        self.loc2 = loc2
        
    def copy(self):
        return LocationRange(self.loc1.copy(), self.loc2.copy())
        
    def tidy(self):
        returnRange = self.copy()
        
        if returnRange.loc1.row > returnRange.loc2.row:
            returnRange.loc1, returnRange.loc2 = returnRange.loc2, returnRange.loc1
        elif returnRange.loc1.row == returnRange.loc2.row and returnRange.loc1.column > returnRange.loc2.column:
            returnRange.loc1, returnRange.loc2 = returnRange.loc2, returnRange.loc1
        
        return returnRange

class EditAction_Added:
    def __init__(self, text, locRange, textModel):
        self.text = text
        self.locRange = locRange
        self.textModel = textModel
        
    def execute_do(self):
        self.textModel.insertString(self.text, True, self.locRange.loc1)
        
    def execute_undo(self):
        self.textModel.deleteRange(self.locRange, True)
        
class EditAction_Deleted:
    def __init__(self, text, locRange, textModel):
        self.text = text
        self.locRange = locRange
        self.textModel = textModel
        
    def execute_do(self):
        self.textModel.deleteRange(self.locRange, True)
        
    def execute_undo(self):
        self.textModel.insertString(self.text, True, self.locRange.loc1)
        

class EditAction_CombineLines:
    def __init__(self, loc, textModel):
        self.row = loc.row
        self.col = loc.column
        self.textModel = textModel
        
    def execute_do(self):
        self.textModel.combineLines(self.row)
        
    def execute_undo(self):
        self.textModel.splitLines(Location(self.row, self.col))
        
class EditAction_SplitLines:
    def __init__(self, loc, textModel):
        self.row = loc.row
        self.col = loc.column
        self.textModel = textModel
        
    def execute_do(self):
        self.textModel.splitLines(Location(self.row, self.col))
        
    def execute_undo(self):
        self.textModel.combineLines(self.row)   
        

        

class ClipboardStack:
    def __init__(self):
        self.texts = []
        self.observers = []
        
    def push(self, text):
        self.texts.append(text)
        self.notifyObservers()
        return
        
    def top(self):
        if not self.texts:
            return None
        return self.texts[-1]
    
    def pop(self):
        if not self.texts:
            return
        self.texts.pop()
        self.notifyObservers()
        return
    
    def notifyObservers(self):
        for observer in  self.observers:
            observer.updateClipboard()
        return
    
    def subscribe(self, sub):
        self.observers.append(sub)
    
    def empty(self):
        return (len(self.texts) == 0)
    
    
class UndoManager:
    _instance = None
    
    def __init__(self):
        if UndoManager._instance is None:
            UndoManager._instance = self
            
            self.undoStack = []
            self.redoStack = []
            self.observers = []
        return
        #else:
        #    print("ne moze")
        
    def emptyFunM(self):
        print("tu")
        return
    
    def undo(self, event = None):
        if not self.undoStack:
            return
        
        command = self.undoStack.pop()
        self.redoStack.append(command)
        command.execute_undo()
        self.notifyObservers()
        return
    
    def push(self, c):
        del[self.redoStack]
        self.redoStack = []
        self.undoStack.append(c)
        self.notifyObservers()
        return
    
    def redo(self, event = None):
        if not self.redoStack:
            return
        
        command = self.redoStack.pop()
        self.undoStack.append(command)
        command.execute_do()
        self.notifyObservers()
        return
    
    def subscribeUndo(self, sub):
        self.observers.append(sub)
    
    def notifyObservers(self):
        UndoNotEmpty = not not self.undoStack
        RedoNotEmpty = not not self.redoStack
        for observer in self.observers:
            observer.updateUndoRedo(UndoNotEmpty, RedoNotEmpty)
        return
    
    def emptyAll(self):
        del[self.undoStack]
        del[self.redoStack]
        self.undoStack = []
        self.redoStack = []
        self.notifyObservers()
    
    @staticmethod
    def instance():
        if UndoManager._instance is None:
            UndoManager()
        return UndoManager._instance
    
    
class TextEditorModel:
    
    def __init__(self, startText):
        self.lines =startText.splitlines()
        self.cursorLocation = Location(1,1)
        self.selectionRange = None
        self.cursorObservers = []
        self.textObservers = []
        self.selectionObservers = []
        self.shiftDown = False
       
    def allLines(self):
        return iter(self.lines)
    
    def linesRange(self, index1, index2):
        return iter(self.lines[index1:index2])
        
    def notifyCursorObservers(self):
        for observer in self.cursorObservers:
            observer.updateCursorLocation(self.cursorLocation)
        return
    
    def notifySelectionObservers(self):
        for observer in self.selectionObservers:
            if self.selectionRange is None:
                observer.updateSelection(None)
            else:
                observer.updateSelection(self.selectionRange.tidy())
        return
    
    def subCursorObserver(self, subscriber):
        self.cursorObservers.append(subscriber)
        return
    
    def subSelectionObserver(self, subscriber):
        self.selectionObservers.append(subscriber)
        return
    
    def moveCursorLeft(self,event):
        if self.cursorLocation.column <= 0:
            return
        
        if self.selectionRange is not None and not self.shiftDown:
            self.selectionRange = None
            self.notifySelectionObservers()
        
        self.cursorLocation.column -= 1
        self.notifyCursorObservers()
        
    def moveCursorRight(self, event):
        if self.cursorLocation.column >= len(self.lines[self.cursorLocation.row]):
            return
        
        if self.selectionRange is not None and not self.shiftDown:
            self.selectionRange = None
            self.notifySelectionObservers()
        
        self.cursorLocation.column += 1
        self.notifyCursorObservers()
        
    def moveCursorUp(self, event):
        if self.cursorLocation.row <= 0:
            return
        
        if self.selectionRange is not None and not self.shiftDown:
            self.selectionRange = None
            self.notifySelectionObservers()
        
        self.cursorLocation.row-=1
        self.cursorLocation.column = min(len(self.lines[self.cursorLocation.row]), self.cursorLocation.column)
        self.notifyCursorObservers()
        
    def moveCursorDown(self, event):
        if self.cursorLocation.row >= (len(self.lines)-1):
            return
        
        if self.selectionRange is not None and not self.shiftDown:
            self.selectionRange = None
            self.notifySelectionObservers()
            
        self.cursorLocation.row += 1
        self.cursorLocation.column = min(len(self.lines[self.cursorLocation.row]), self.cursorLocation.column)
        self.notifyCursorObservers()
        
        
    def subTextObserver(self, sub):
        self.textObservers.append(sub)
        return
    
    def notifyTextObservers(self):
        for sub in self.textObservers:
            sub.updateText()
        
    def combineLines(self, row):
        if row >= len(self.lines):
            return
        
        oldSize = len(self.lines[row])
        
        self.lines[row] += self.lines[row+1]
        del[self.lines[row+1]]
        self.notifyTextObservers()
        self.setCursorLocation(Location(row, oldSize))
        return
    
    def splitLines(self, Loc):
        row = Loc.row
        col = Loc.column
        
        self.lines.insert(row+1, self.lines[row][col:])
        self.lines[row] = self.lines[row][:col]
        self.notifyTextObservers()
        self.setCursorLocation(Location(row+1, 0))
        
        return
        
    def deleteRange(self, r, UndoRedo = False):
        start = r.loc1
        end = r.loc2
        text = self.getSelectionText(r)
        self.lines[start.row]= self.lines[start.row][:start.column] +  self.lines[end.row][end.column:]
        del[self.lines[start.row+1:end.row+1]]
        self.selectionRange = None
        self.notifySelectionObservers()
        self.notifyTextObservers()
        self.setCursorLocation(start)
        if not UndoRedo:
            UndoManager.instance().push(EditAction_Deleted(text, r, self))
            #print(len(UndoManager.instance().undoStack))
        #print(r.loc1.row)
        #print(r.loc1.column)
        #print(r.loc2.row)
        #print(r.loc2.column)
        return
        
    def deleteBefore(self, event = None):
        
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange.tidy())
            return
        
        if self.cursorLocation.column <= 0:
            if self.cursorLocation.row <= 0:
                return
            self.combineLines(self.cursorLocation.row-1)
            UndoManager.instance().push(EditAction_CombineLines(self.cursorLocation, self))
        else:
                
            delCol= self.cursorLocation.column - 1
            delRow = self.cursorLocation.row
            delChar = self.lines[delRow][delCol]
            self.lines[delRow] = self.lines[delRow][:delCol] + self.lines[delRow][delCol+1:]
            UndoManager.instance().push(EditAction_Deleted(delChar, LocationRange(Location(delRow,delCol),Location(delRow,delCol+1)), self))
            self.notifyTextObservers()    
            self.moveCursorLeft(None)
        
        return
        
    def deleteAfter(self, event = None):
        
        if self.selectionRange is not None:
           # print(self.getSelectionText())
            self.deleteRange(self.selectionRange.tidy())
            return
        
        
        if self.cursorLocation.column >= (len(self.lines[self.cursorLocation.row])):
            if self.cursorLocation.row == len(self.lines)-1:
                return
            #self.lines[self.cursorLocation.row] += self.lines[self.cursorLocation.row+1]
            #del[self.lines[self.cursorLocation.row+1]]
            self.combineLines(self.cursorLocation.row)
            UndoManager.instance().push(EditAction_CombineLines(self.cursorLocation, self))
    
        else:
            delCol= self.cursorLocation.column
            delRow = self.cursorLocation.row
            delChar = self.lines[delRow][delCol]
            self.lines[delRow] = self.lines[delRow][:delCol] + self.lines[delRow][delCol+1:]
            UndoManager.instance().push(EditAction_Deleted(delChar, LocationRange(Location(delRow,delCol),Location(delRow,delCol)), self))
        self.notifyTextObservers()
        self.notifyCursorObservers()
    
    
    def keyInsert(self, event):
        #print(event.keysym)
        if event.keysym == 'Return':
            self.insert("\n")
        else:    
            c = event.char
            if len(c) == 1:
                self.insert(c)
        return
    
    def insert(self, c):
        
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange.tidy())
        
        row = self.cursorLocation.row
        col = self.cursorLocation.column
        #print(c)
        if c == '\n':
            UndoManager.instance().push(EditAction_SplitLines(self.cursorLocation, self))
            self.splitLines(self.cursorLocation)

        else:
            self.lines[row] = self.lines[row][:col] + c + self.lines[row][col:]
            UndoManager.instance().push(EditAction_Added(c, LocationRange(Location(row,col),Location(row,col+1)), self))
            self.notifyTextObservers()
            self.moveCursorRight(None)
        return
    
    def insertString(self, string, UndoRedo = False, customLoc = None):
        #if len(string) == 1:
        #    self.insert(string)
        #    return
        
        if self.selectionRange is not None:
            self.deleteRange(self.selectionRange.tidy())
        
        
        if customLoc is None:
            row = self.cursorLocation.row
            col = self.cursorLocation.column
        else:
            row =  customLoc.row
            col =  customLoc.column
        
        strLines = string.splitlines()
        
        suffix = self.lines[row][col:]
        self.lines[row] = self.lines[row][:col] + strLines[0]
        
        rowNow = row +1
        for line in strLines[1:]:
            self.lines.insert(rowNow, line)
            rowNow+=1
        
        cursorPos = len(self.lines[rowNow -1])
        self.lines[rowNow -1] += suffix
        
        self.notifyTextObservers()
        newCursorLoc = Location(rowNow-1, cursorPos)
        self.setCursorLocation(newCursorLoc)
        
        if not UndoRedo:
            UndoManager.instance().push(EditAction_Added(string, LocationRange(Location(row,col), newCursorLoc), self))
        
        return
    
    
    def moveCursorToStart(self):
        self.cursorLocation = Location(0,0)
        self.notifyCursorObservers()
        return
    
    
        
    def moveCursorToEnd(self):
        self.cursorLocation = Location(len(self.lines)-1,len(self.lines[-1]))
        self.notifyCursorObservers()
        return
    
    
    def setCursorLocation(self, loc):
        #del[self.cursorLocation]
        self.cursorLocation = loc.copy()
        self.notifyCursorObservers()
        return
    
    def handleShift(self, event):
    
        if self.selectionRange is None:
            self.selectionRange = LocationRange(self.cursorLocation, self.cursorLocation.copy())

        self.shiftDown = True
        
        if event.keysym == 'Up':
            self.moveCursorUp(None)
        elif event.keysym == 'Down':
            self.moveCursorDown(None)
        elif event.keysym == 'Left':
            self.moveCursorLeft(None)
        elif event.keysym == 'Right':
            self.moveCursorRight(None)
        
        self.shiftDown = False
        
        self.notifySelectionObservers()
    
    
    def getSelectionText(self, customRange = None):
        if self.selectionRange is None:
            return ""
        
        tempRange = None
        
        if customRange is None:
            tempRange = self.selectionRange.tidy()
        else:
            tempRange = customRange.tidy()
        
        
        start = tempRange.loc1
        end = tempRange.loc2
        
        if start.row == end.row:
            return self.lines[start.row][start.column:end.column]
        
        
        selectionText = self.lines[start.row][start.column:]
        
        for line in self.lines[start.row+1:end.row]:
            selectionText += "\n"+ line 
        
        selectionText += "\n" + self.lines[end.row][:end.column]
        
        return selectionText
    
    def deleteAll(self):
        #del[self.lines]
        #self.lines = []
        #self.lines.append(" ")
        #self.selectionRange = None
        
        startLoc = Location(0,0)
        endLoc = Location(len(self.lines)-1,len(self.lines[-1]))
        self.deleteRange(LocationRange(startLoc, endLoc).tidy())
        #self.lines = []
        #self.lines.append("")
        
    def setAllText(self, text):
        del[self.lines]
        self.lines= text.splitlines()
        
        self.notifySelectionObservers()
        self.notifyTextObservers()
        self.moveCursorToEnd()
        
    def getAllText(self):
        text = ""
        for line in self.lines:
            text+= line+"\n"
            
        return text
    
    def getLineNumber(self):
        return len(self.lines)
    
    def getWordNumber(self):
        wordNum = 0
        for line in self.lines:
            wordNum += len(line.split())
        return wordNum
    
    def getLetterNumber(self):
        return len(self.getAllText().split())
            
        
    
def checkFun(event):
    print("TU SAM")
    return
    
class TextEditor(Canvas):
    
    def __init__(self, root, textModel, fontText):
        self.root = root
        self.textModel = textModel
        super().__init__(self.root)
        
        self.fontText = fontText
        self.letterWidth = self.fontText.measure("a")
        self.letterHeight= self.fontText.metrics("linespace")
        
        self.config(height = 1000)
        
        
        ## POVEZIVANJE KOMANDI STRELICA
        self.root.bind('<Left>', self.textModel.moveCursorLeft)
        self.root.bind('<Right>', self.textModel.moveCursorRight)
        self.root.bind('<Up>', self.textModel.moveCursorUp)
        self.root.bind('<Down>', self.textModel.moveCursorDown)
        self.textModel.subCursorObserver(self)
        
        self.root.bind('<BackSpace>', self.textModel.deleteBefore)
        self.root.bind('<Delete>', self.textModel.deleteAfter)
        self.root.bind('<Shift-Up>', self.textModel.handleShift)
        self.root.bind('<Shift-Right>', self.textModel.handleShift)
        self.root.bind('<Shift-Down>', self.textModel.handleShift)
        self.root.bind('<Shift-Left>', self.textModel.handleShift)
        self.root.bind('<Key>', self.textModel.keyInsert)
        
        self.root.bind("<Control-c>", self.handleCopy)
        self.root.bind("<Control-x>", self.handleCut)
        self.root.bind("<Control-v>", self.handlePaste)
        self.root.bind("<Control-Shift-V>", self.handlePastePop)
        
        self.root.bind("<Control-z>", UndoManager.instance().undo)
        self.root.bind("<Control-y>", UndoManager.instance().redo)
        
        
        self.textModel.subTextObserver(self)
        
        self.textModel.subSelectionObserver(self)
        
        
        self.clipboard = ClipboardStack()
        
        self.cursorId = None
        self.drawCursor(self.textModel.cursorLocation)
        self.drawText()
        
        self.selectionIds = None
        
    def drawCursor(self, loc):
        if self.cursorId is not None:
            self.delete(self.cursorId)
        
        cursorX = self.letterWidth * loc.column + 2
        cursorYStart = self.letterHeight * loc.row
        
        self.cursorId = self.create_line(cursorX, cursorYStart, cursorX, cursorYStart + self.letterHeight, fill = 'gray', width = 1)
         
    def updateCursorLocation(self, loc):
        self.drawCursor(loc)
        return
    
    
    def drawText(self):
        curRow = 0
        lineIter = self.textModel.allLines()
        while True:
            try:
                line = next(lineIter)
            except StopIteration:
                break
            else:
                 self.create_text(2, curRow * (self.letterHeight) + self.letterHeight / 2, anchor = W, font = self.fontText, text = line)
                 curRow += 1
        
    def drawSelection(self, selection):
        self.delete("all")
        
        start = selection.loc1
        end = selection.loc2
        lineIter = self.textModel.linesRange(start.row, end.row+1)
        dist = end.row - start.row
        curRow = 0
        
        if self.selectionIds is not None:
            del(self.selectionIds)
        self.selectionIds = []
        
        
        while True:
            try:
                line = next(lineIter)
            except StopIteration:
                break
            else:
                rectStartX = 2
                rectEndX = len(line) * self.letterWidth + 2 
                rectY = (curRow+start.row)*(self.letterHeight) #+self.letterHeight/2
                if curRow == 0:
                    rectStartX = self.letterWidth * start.column + 2
                if curRow == dist:
                    rectEndX = self.letterWidth * end.column + 2
                
                self.selectionIds.append(self.create_rectangle(rectStartX, rectY, rectEndX, rectY + self.letterHeight, fill = "grey", outline = ""))
                self.tag_lower(self.selectionIds[-1])
                self.tag_lower(self.selectionIds[-1])
                curRow+=1
                
        self.drawText()
        
    def updateText(self):
        self.delete("all")
        self.drawText()
        return
    
    def updateSelection(self, selection):
        if selection is None:
            if self.selectionIds is not None:
                for rectId in self.selectionIds:
                    self.delete(rectId)
                del(self.selectionIds)
                self.selectionIds = None
            
        else:
            self.drawSelection(selection)
        return
    
    def handleCopy(self, event = None):
        
        if self.textModel.selectionRange is None:
            return
        
        self.clipboard.push(self.textModel.getSelectionText())
        
        return
    
    def handleCut(self, event = None):
        
        if self.textModel.selectionRange is None:
            return
        
        self.clipboard.push(self.textModel.getSelectionText())
        self.textModel.deleteAfter(None)
        return
    
    def handlePaste(self, event = None):
        
        if self.clipboard.empty():
            return
        
        text = self.clipboard.top()
        
        self.textModel.insertString(text)
        
        return
    
    def handlePastePop(self, event = None):
        
        if self.clipboard.empty():
            return
        
        text = self.clipboard.top()
        self.clipboard.pop()
        
        self.textModel.insertString(text)
        return
    
        
def emptyFun(event):
    return
        

class TE_Statusbar(Label):
    def __init__(self, root, textModel, statusFont):
        self.root = root
        self.textModel = textModel
        self.textModel.subCursorObserver(self)
        
        super().__init__(root, font = statusFont, text = "", relief  = SUNKEN, bd = 1, anchor = W)
        self.updateCursorLocation(textModel.cursorLocation)
        
    def updateCursorLocation(self, loc):
        self.config(text = "Cursor location: row: {:3}column: {:3}  Total lines: {}".format(str(loc.row+1),str(loc.column+1), str(len(self.textModel.lines))))
       
        

class TE_Toolbar(Frame):
    def __init__(self, root, textModel, textEditor, fontToolbar):
        self.root = root
        self.fontToolbar = fontToolbar
        self.textModel = textModel
        self.textEditor = textEditor
        super().__init__(root, bd = 2, relief = FLAT)
            
        self.undoButton = Button(self, text = "Undo", font = self.fontToolbar, relief = FLAT, command = UndoManager.instance().undo, state = "disabled")
        self.undoButton.pack(side = LEFT, padx = 4)
        
        self.redoButton = Button(self,text = "Redo", font = self.fontToolbar, relief = FLAT, command =  UndoManager.instance().redo, state = "disabled")
        self.redoButton.pack(side = LEFT, padx = 4)
        
        self.cutButton = Button(self, text = "Cut", font = self.fontToolbar, relief = FLAT, command = self.textEditor.handleCut, state = "disabled")
        self.cutButton.pack(side = LEFT, padx = 4)

        self.copyButton = Button(self, text = "Copy", font = self.fontToolbar, relief = FLAT, command = self.textEditor.handleCopy, state = "disabled")
        self.copyButton.pack(side = LEFT, padx = 4)
        
        self.pasteButton = Button(self, text = "Paste", font = self.fontToolbar, relief = FLAT, command = self.textEditor.handlePaste, state = "disabled")
        self.pasteButton.pack(side = LEFT, padx = 4)
        
        
        self.textModel.subSelectionObserver(self)
        self.textEditor.clipboard.subscribe(self)
        UndoManager.instance().subscribeUndo(self)
        
    def updateSelection(self, selectionRange):
        if selectionRange is None:
            self.cutButton.config(state = "disabled")
            self.copyButton.config(state = "disabled")
        else:
            self.cutButton.config(state = "active")
            self.copyButton.config(state = "active")
            
        return
        
    def updateClipboard(self):
        if self.textEditor.clipboard.empty():
            self.pasteButton.config(state = "disabled")
        else:
            self.pasteButton.config(state = "active")
        return
    
    def updateUndoRedo(self, UndoNotEmpty, RedoNotEmpty):
        if UndoNotEmpty:
            self.undoButton.config(state = "active")
        else:
            self.undoButton.config(state = "disabled")
            
        if RedoNotEmpty:
            self.redoButton.config(state = "active")
        else:
            self.redoButton.config(state = "disabled")


def pluginFactory(pluginName):
    plugin = importlib.import_module('plugins.' + pluginName)
    return getattr(plugin, "create")
        
    
class TE_Menu(Menu):
     def __init__(self, root, textModel, textEditor, plugins):
        self.root = root
        self.textModel = textModel
        self.textEditor = textEditor
        self.plugins = plugins
         ## MENU GORE
        super().__init__(self.root)
        
        ## FILE MENU
        self.fileMenu = Menu(self, tearoff = False)
        self.fileMenu.add_command(label = "Open", command = self.loadFun)
        self.fileMenu.add_command(label = "Save", command = self.saveFun)
        self.fileMenu.add_command(label = "Exit", command = self.exitFun)
        self.add_cascade(label = "File", menu = self.fileMenu)
        
        ## EDIT MENU
        self.editMenu = Menu(self, tearoff = False)
        self.editMenu.add_command(label = "Undo", command = UndoManager.instance().undo, state = "disabled")
        self.editMenu.add_command(label = "Redo", command = UndoManager.instance().redo, state = "disabled")
        self.editMenu.add_command(label = "Cut", command = self.textEditor.handleCut, state = "disabled")
        self.editMenu.add_command(label = "Copy", command =  self.textEditor.handleCopy, state = "disabled")
        self.editMenu.add_command(label = "Paste", command =  self.textEditor.handlePaste, state = "disabled")
        self.editMenu.add_command(label = "Paste and Take", command = self.textEditor.handlePastePop, state = "disabled")
        self.editMenu.add_command(label = "Delete selection", command = self.textModel.deleteAfter, state = "disabled")
        self.editMenu.add_command(label = "Clear document", command = self.textModel.deleteAll)
        self.add_cascade(label = "Edit", menu = self.editMenu)
        
        ## MOVE MENU
        self.moveMenu = Menu(self, tearoff = False)
        self.moveMenu.add_command(label = "Cursor to document start", command = self.textModel.moveCursorToStart)
        self.moveMenu.add_command(label = "Cursor to document end", command = self.textModel.moveCursorToEnd)
        self.add_cascade(label = "Move", menu = self.moveMenu)
        
        ## PLUGINS
        self.pluginMenu = Menu(self,tearoff = False)
        for plugin in self.plugins:
            fun = plugin.execute
            #self.pluginMenu.add_command(label = plugin.getName(), command = lambda: plugin.execute(self.textModel, UndoManager.instance()))
            self.pluginMenu.add_command(label = plugin.getName(), command = lambda fun = fun: fun(self.textModel, UndoManager.instance()))
        
        self.add_cascade(label = "Plugins", menu = self.pluginMenu)
        
        self.textModel.subSelectionObserver(self)
        self.textEditor.clipboard.subscribe(self)
        UndoManager.instance().subscribeUndo(self)
        
     def updateSelection(self, selectionRange):
        if selectionRange is None:
            self.editMenu.entryconfig("Cut",state = "disabled")
            self.editMenu.entryconfig("Copy",state = "disabled")
            self.editMenu.entryconfig("Delete selection",state = "disabled")
            #self.editMenu.entryconfig("Cut",state = "disabled")
            
        else:
            self.editMenu.entryconfig("Cut",state = "active")
            self.editMenu.entryconfig("Copy",state = "active")
            self.editMenu.entryconfig("Delete selection",state = "active")
            
        return
        
     def updateClipboard(self):
        if self.textEditor.clipboard.empty():
            self.editMenu.entryconfig("Paste",state = "disabled")
            self.editMenu.entryconfig("Paste and Take",state = "disabled")
        else:
            self.editMenu.entryconfig("Paste",state = "active")
            self.editMenu.entryconfig("Paste and Take",state = "active")
        return

     def exitFun(self):
        self.root.destroy()
        return
    
     def loadFun(self):
        with open("input.txt", 'r') as inputFile:
            self.textModel.setAllText(inputFile.read())
            UndoManager.instance().emptyAll()
            
     def saveFun(self):
         with open("output.txt", 'w') as outputFile:
             outputFile.write(self.textModel.getAllText())
            
            
     def updateUndoRedo(self, UndoNotEmpty, RedoNotEmpty):
        if UndoNotEmpty:
            self.editMenu.entryconfig("Undo",state = "active")
        else:
            self.editMenu.entryconfig("Undo",state = "disabled")
            
        if RedoNotEmpty:
            self.editMenu.entryconfig("Redo",state = "active")
        else:
            self.editMenu.entryconfig("Redo",state = "disabled")
    

def main():
    root = Tk()
    root.title("NOTEPAD")
    root.geometry("1200x700")
    undoManager = UndoManager.instance()
    
    fontToolbar = font.Font(family = 'Courier New', size  = 13)
    fontText = font.Font(family = "Courier New", size = 12)
    fontStatus = font.Font(family = "Courier New", size = 10)
    
    ## TEXT EDITOR
    startText = "Dobrodosli u jednostavni text editor!\nOvo je primjer pocetka programa i ovo su neke linije.\nHrvoje"
    textModel = TextEditorModel(startText)
    textEditor = TextEditor(root, textModel, fontText)
    
    textEditPadLeft = 10
    textEditPadTop = 10

    ## PLUGINS
    plugins = []
    for file in os.listdir('plugins'):
        fileName, fileExt = os.path.splitext(file)
        if fileExt == '.py':
            plugin = pluginFactory(fileName)()
            plugins.append(plugin)
    
    ## MENU GORE
    textEditorMenu = TE_Menu(root, textModel, textEditor, plugins)
    root.config(menu= textEditorMenu)
    
    
    ### TOOLBAR
    toolbar = TE_Toolbar(root, textModel, textEditor, fontToolbar)
    toolbar.pack(side = TOP, fill = X)
        
    
    ## STATUS BAR
    statusBar = TE_Statusbar(root, textModel, fontStatus)
    statusBar.pack(side = BOTTOM, fill = X)

    textEditor.pack(side = TOP, fill = BOTH, padx = textEditPadLeft, pady = textEditPadTop,  expand = YES)
    
    
    root.mainloop()
    
    
main()