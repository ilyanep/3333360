import pygame, sys, os, random, math
from pygame.locals import *

class threeSixtyAI ():
    def __init__(self, inputMap, curPos, rivalPos):
        self.makeBetterMap(inputMap)
        
        self.numMoves = 0
        self.curAction = 'D'
        self.untilRandom = -1
        self.graphify(betterMap)
        #self.floydWarshall(inputMap)

    #Puts the map into a better form
    def makeBetterMap(self, map):
        self.maxFirst = 0
        self.maxSecond = 0

        #Find the dimensions of the board because they're given to us as 
        #a goddamn dictionary
        for i in map.iterkeys():
            if i[0] > self.maxFirst:
                self.maxFirst = i[0]
            if i[1] > self.maxSecond:
                self.maxSecond = i[1]

        self.betterMap = []
        for i in range(self.maxFirst):
            self.betterMap.append([])
            for j in range(self.maxSecond):
                self.betterMap[i].append(map[(i,j)])

    #Take the map and turn it into a graph where the junction points (more than one way to go) are nodes
    def graphify(self, map):
        self.junctions = []
        self.reverseJunctions = {}
        #Find junctions
        for i in range(self.maxFirst):
            for j in range(self.maxSecond):
                degree = 0
                if validCoord(i,j+1) and not isWall(self.betterMap[i][j+1]):
                    degree = degree + 1
                if validCoord(i,j-1) and not isWall(self.betterMap[i][j-1]):
                    degree = degree + 1
                if validCoord(i-1,j) and not isWall(self.betterMap[i-1][j]):
                    degree = degree + 1
                if validCoord(i+1,j) and not isWall(self.betterMap[i+1][j]):
                    degree = degree + 1
                if degree > 2 or degree == 1:
                    self.junctions.append((i,j))
                    self.reverseJunctions[(i,j)] = len(junctions)-1 

        #Create adjacency matrix for junctions
        self.junctAdj = []
        for i in range(len(self.junctions)):
            self.junctAdj.append([])
            for j in range(len(self.junctions)):
                self.junctAdj[i].append(0)

        for i in range(len(self.junctions)):
            #Expand Right
            x,y = self.junctions[i]
            dir = 'R'
            canGo = self.validCoord(i+1,j) and not self.isWall(self.betterMap[i+1][j])
            pathLength = 0
            while canGo:
                pathLength = pathLength+1
                if dir='R':
                    x = x+1
                    if (x,y) in self.junctions:
                        self.junctAdj[reverseJunctions[(x,y)]][i] = pathLength
                    else:
                        if self.validCoord(i+1,j)
                elif dir='L':
                elif dir='U':
                elif dir='D':
            #Expand Up
            #Expand Left
            #Expand Down

    def firstCoord(self, value):
        return int(value / self.maxSecond)

    def secondCoord(self, value):
        return (value % self.maxSecond)

    def validCoord(self, x, y):
        return (x >= 0) and (y >= 0) and (x <= self.maxFirst) and (y <= self.maxSecond)

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
