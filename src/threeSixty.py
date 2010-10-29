import pygame, sys, os, random, math
from pygame.locals import *

class threeSixtyAI ():
    def __init__(self, inputMap, curPos, rivalPos):
        self.numMoves = 0
        self.curAction = 'D'
        self.untilRandom = -1
        self.floydWarshall(inputMap)

#----------Floyd-Warshall Algorithm-----------#
    def floydWarshall(self, map):
        self.maxFirst = 0
        self.maxSecond = 0

        #Find the dimensions of the board because they're given to us as 
        #a goddamn dictionary
        for i in map.iterkeys():
            if i[0] > self.maxFirst:
                self.maxFirst = i[0]
            if i[1] > self.maxSecond:
                self.maxSecond = i[1]
        

        #All-pairs shortest paths (The node at row,col is (row*maxCol)+col)
        #Initiate array:
        aBigNumber = self.maxFirst*self.maxSecond*self.maxFirst*self.maxSecond
        self.allPairsShortestPath = []
        for i in range(self.maxFirst*self.maxSecond):
            self.allPairsShortestPath.append([])
            for j in range(self.maxFirst*self.maxSecond):
                self.allPairsShortestPath[i].append([])

        #Initial Values:
        for i in range(self.maxFirst*self.maxSecond):
            for j in range(self.maxFirst*self.maxSecond):
                if j == i-1 and not self.isWall(map[(self.firstCoord(j), self.secondCoord(j))]):
                    self.allPairsShortestPath[i][j] = 1
                elif j == i+1 and not self.isWall(map[(self.firstCoord(j), self.secondCoord(j))]):
                    self.allPairsShortestPath[i][j] = 1
                elif j == (i - self.maxFirst) and not self.isWall(map[(self.firstCoord(j), self.secondCoord(j))]):
                    self.allPairsShortestPath[i][j] = 1
                elif j == (i + self.maxFirst) and not self.isWall(map[(self.firstCoord(j), self.secondCoord(j))]):
                    self.allPairsShortestPath[i][j] = 1
                else:
                    self.allPairsShortestPath[i][j] = aBigNumber

        #Run algorithm:
        for k in range(self.maxFirst*self.maxSecond):
            if self.isWall(map[(self.firstCoord(k), self.secondCoord(k))]):
                continue
            print k
            for i in range(self.maxFirst*self.maxSecond):
                if self.isWall(map[(self.firstCoord(i), self.secondCoord(i))]):
                    continue
                for j in range(self.maxFirst*self.maxSecond):
                    if self.isWall(map[(self.firstCoord(j), self.secondCoord(j))]):
                        continue
                    self.allPairsShortestPath[i][j] = min(self.allPairsShortestPath[i][j], \
                        self.allPairsShortestPath[i][k] + self.allPairsShortestPath[k][j])
#----------End really long block of code I hate Python---------#
    def firstCoord(self, value):
        return int(value / self.maxSecond)

    def secondCoord(self, value):
        return (value % self.maxSecond)

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
