# -*- coding: utf-8 -*-
"""
Created on Mon May 13 17:28:18 2019

@author: yimin
"""
import random
import sys
from PyQt5.QtWidgets import (QWidget, 
    QPushButton, QApplication, QGridLayout, QMessageBox, QLabel) 
from PyQt5 import QtCore
from functools import partial

"""--------Back End-------"""
class Button(object):
    def __init__(self, r, c):
        self.coords = (r, c)
        self.mine = False
        self.surroundingMines = 0
        self.opened = False
    def openNotMine(self):
        self.opened = True
    def __repr__(self): #for troubleshooting purposes
        return 'Button ({}, {}) is {}a mine with {} surrounding mines.'\
            .format(self.coords[0], self.coords[1],
            '' if self.mine else 'not ', self.surroundingMines)
        """return str(self.mine)"""
        """return str(self.opened)"""

class Grid(object):
    total_opened = 0 #if this reaches 90, the player wins
    def __init__(self): #instance attributes: .grid, .allMines
        self.initGrid()
        self.generateMines()
        self.initSurroundingMines()
        
    def initGrid(self): #create empty buttons in the grid
        self.grid = list()
        for i in range(10):
            row = list()
            for j in range(10):
                row.append(Button(i, j))
            self.grid.append(row)
    
    def generateMines(self): #create mine locations and change attributes of the buttons with mines
        self.allMines = list()
        while len(self.allMines) < 10:
            mineLoc = (random.randint(0, 9), random.randint(0, 9))
            if mineLoc not in self.allMines:
                self.allMines.append(mineLoc)
        for r, c in self.allMines:
            self.grid[r][c].mine = True

    def nSurroundingMines(self, r, c):
        nMines = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                r_ = r + i
                c_ = c + j
                if r_ > -1 and r_ < 10 and c_ > -1 and c_ < 10: #check all surrounding mines if not out of grid, including the button itself
                    nMines = nMines + 1 if self.grid[r_][c_].mine else nMines
        nMines = nMines - 1 if self.grid[r][c].mine else nMines #remove the button itself
        return nMines
    
    def initSurroundingMines(self):
        for row in self.grid:
            for button in row:
                r, c = button.coords
                button.surroundingMines = self.nSurroundingMines(r, c)
    
    def open_(self, r, c):
        if self.grid[r][c].mine == True:
            self.grid[r][c].opened = True
            self.openedMine()
            return 'Mine'
        else:
            val = self.grid[r][c].surroundingMines
            if val == 0:
                self.openedBlank(r, c)
            else:
                self.grid[r][c].opened = True; Grid.total_opened = Grid.total_opened + 1
            return '' if val == 0 else str(val)
    
    #def openedMine(self):
    
    def openedBlank(self, r, c): #blank refers to having no mines around
        if self.grid[r][c].opened == False: #not opened means not visited (prevents loops)
            self.grid[r][c].opened = True; Grid.total_opened = Grid.total_opened + 1 #open
            if self.grid[r][c].surroundingMines == 0:
                try:
                    for i in range (-1, 2):
                        for j in range (-1, 2):
                            r_ = r + i
                            c_ = c + j
                            if r_ > -1 and r_ < 10 and c_ > -1 and c_ < 10:
                                self.openedBlank(r_, c_) #check if surrounding is blank
                except:
                    pass
    
    def printGrid(self):
        for row in self.grid:
            for button in row:
                print(button.surroundingMines, sep = '', end = '\t')
            print('')
    
    def visibleGrid(self):
        vGrid = list()
        for row in self.grid:
            temp = list()
            for button in row:
                if button.opened == True:
                    if button.mine == False:
                        temp.append(str(button.surroundingMines))
                    else:
                        temp.append('*') #mine
                else:
                    temp.append('') #not opened
            vGrid.append(temp)
        return vGrid.copy()
    
    def openedMine(self):
        for mine_r, mine_c in self.allMines:
                self.grid[mine_r][mine_c].opened = True

#a = Grid()
def test(a, r, c): #to test backend
    print('You opened a {}'.format(a.open_(r, c)))
    z = a.visibleGrid()
    for y in z:
        print(y)
    print('Total opened: {}'.format(a.total_opened))

"""-------Front-end GUI------"""

class Minesweeper(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):   
        btn_x = 100
        btn_y = 100
        self.allButtons = list() #list of list of buttons
        self.backEnd = Grid() #create backend grid
        for i in range (10):
            temp = list()
            for j in range (10):
                btn = QPushButton(self.backEnd.visibleGrid()[i][j], self)
                btn.clicked.connect(partial(self.button_click, i, j)) #or btn.clicked.connect(self.button_click_closure(i, j))
                btn.resize(20, 20)
                btn.move(btn_x + i * 20, btn_y + j * 20)
                temp.append(btn);
            self.allButtons.append(temp)
        
        reset_btn = QPushButton('Reset', self)
        reset_btn.resize(60, 20)
        reset_btn.move(170, 40)
        reset_btn.clicked.connect(self.reset)
        
        self.lbl = QLabel(self)
        self.lbl.setGeometry(QtCore.QRect(104, 66, 160, 36)) #(x, y, width, height)
        self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nNon-mine squares left: 90")
#        self.lbl.move(100, 80)
        
        self.setGeometry(300, 300, 400, 350)
        self.setWindowTitle("Yi-Min's Minesweeper") 
        self.show()
    
    """def button_click_closure(self, r, c): #function closure method alternative to functools.partial
        def button_click():
            print('r: {}, c: {}'.format(r, c)) #for testing purposes
            gameLose = False
            total_opened = 0
            if self.backEnd.grid[r][c].opened == False:
                self.backEnd.open_(r, c)
                self.updateApp()
                newGrid = self.backEnd.visibleGrid()
                for i in range(10):
                    for j in range(10):
                        text = newGrid[i][j]
                        if text =='*':
                            gameLose = True
                        elif text != '':
                            total_opened = total_opened + 1
                self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nNon-mine squares left: {}".format(str(90 - total_opened))) #Update how many squares left
                if gameLose == True: #check if lose
                    print('Game Over: You lose!')
                    self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nYou lose!")
                    QMessageBox.about(self, "Loser!", "You lost! Click Ok to reset")
                    self.reset()
                elif total_opened == 90: #check if win
                    print('Game Over: You Win!')
                    self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nYou win!")
                    QMessageBox.about(self, "Winner!", "You won! Click Ok to reset")
                    self.reset()
        return button_click"""
    
    def button_click(self, r, c):
        print('r: {}, c: {}'.format(r, c)) #for testing purposes
        gameLose = False
        total_opened = 0
        if self.backEnd.grid[r][c].opened == False:
            self.backEnd.open_(r, c)
            self.updateApp()
            newGrid = self.backEnd.visibleGrid()
            for i in range(10):
                for j in range(10):
                    text = newGrid[i][j]
                    if text =='*':
                        gameLose = True
                    elif text != '':
                        total_opened = total_opened + 1
            self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nNon-mine squares left: {}".format(str(90 - total_opened))) #Update how many squares left
            if gameLose == True: #check if lose
                print('Game Over: You lose!')
                self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nYou lose!")
                QMessageBox.about(self, "Loser!", "You lost! Click Ok to reset")
                self.reset()
            elif total_opened == 90: #check if win
                print('Game Over: You Win!')
                self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nYou win!")
                QMessageBox.about(self, "Winner!", "You won! Click Ok to reset")
                self.reset()
                
    def updateApp(self):
        newGrid = self.backEnd.visibleGrid()
        print(newGrid) #for testing purposes
        for i in range(10):
            for j in range(10):
                text = newGrid[i][j]
                self.allButtons[i][j].setText(text)
    
    def reset(self):
        self.backEnd = Grid() #initialize new grid
        self.updateApp()
        self.lbl.setText("Welcome to Yi-Min's Minesweeper!\nNon-mine squares left: 90")
                       
app = QApplication(sys.argv)
ex = Minesweeper()
sys.exit(app.exec_())