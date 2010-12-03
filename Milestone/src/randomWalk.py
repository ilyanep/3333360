import pygame, sys, os, random, math
from pygame.locals import *

class randomWalkAI ():
    def __init__(self, inputMap, curPos, rivalPos, mapHeight, mapWidth):
        self.curAction = 'D'
        
    def think(self, curMap, curPos, rivalPos, curGraceTime):
        curRow, curCol = curPos
        self.possibleAction = []
        
        if not 100<=curMap[curRow, curCol+1]<=199:
            self.possibleAction.append('R')
        if not 100<=curMap[curRow, curCol-1]<=199:
            self.possibleAction.append('L')
        if not 100<=curMap[curRow+1, curCol]<=199:
            self.possibleAction.append('D')
        if not 100<=curMap[curRow-1, curCol]<=199:
            self.possibleAction.append('U')
            
        if len(self.possibleAction)>1:
            if (self.curAction=='R') and ('L' in self.possibleAction):
                self.possibleAction.remove('L')
            if (self.curAction=='L') and ('R' in self.possibleAction):
                self.possibleAction.remove('R')
            if (self.curAction=='U') and ('D' in self.possibleAction):
                self.possibleAction.remove('D')
            if (self.curAction=='D') and ('U' in self.possibleAction):
                self.possibleAction.remove('U')
        
        
        nextAction = random.choice(self.possibleAction)
        self.curAction = nextAction
        return nextAction
