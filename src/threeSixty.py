import pygame, sys, os, random, math
from pygame.locals import *

class threeSixtyAI ():
    def __init__(self, inputMap, curPos, rivalPos):
        self.numMoves = 0
        self.curAction = 'D'
        self.untilRandom = -1

    def isWall(self, value):
        return (100<=value<=199)

    def think(self, curMap, curPos, rivalPos, curGraceTime):
        print curGraceTime
        curRow, curCol = curPos
        if self.numMoves > self.untilRandom:
            self.numMoves = 0
            self.untilRandom = random.randint(1,15)
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
        else:
            if not self.isWall(curMap[curRow-1, curCol]) and ((curRow-1,curCol) != self.lastPos): 
                nextAction = 'U'
            elif not self.isWall(curMap[curRow, curCol+1]) and ((curRow, curCol+1) != self.lastPos):
                nextAction = 'R'
            elif not self.isWall(curMap[curRow, curCol-1]) and ((curRow, curCol-1) != self.lastPos):
                nextAction = 'L'
            elif not self.isWall(curMap[curRow+1, curCol]) and ((curRow+1, curCol) != self.lastPos):
                nextAction = 'D'
        self.lastPos = curPos
        self.numMoves = self.numMoves + 1
        return nextAction
