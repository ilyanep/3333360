import pygame, sys, os, random, math
from pygame.locals import *

class threeSixtyAI ():
    def __init__(self, inputMap, curPos, rivalPos, mapHeight, mapWidth):
        self.makeBetterMap(inputMap)
        
        self.numMoves = 0
        self.curAction = 'D'
        self.untilRandom = -1
        self.graphify(self.betterMap)
        #self.floydWarshall(inputMap)

    def makeBetterMap(self, map):
        '''Takes the map in dict(tuple -> int) form and turns it into a 2D list''' 
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
        for i in range(self.maxFirst+1):
            self.betterMap.append([])
            for j in range(self.maxSecond+1):
                self.betterMap[i].append(map[(i,j)])

    def graphify(self, map):
        '''Compresses the graph of the map into a graph of junction points (degree == 1 or degree > 2)

        Takes the map in 2D list form. Returns nothing. Sets some member variables'''
        self.junctions = []
        self.reverseJunctions = {}
        #Find junctions
        for i in range(self.maxFirst+1):
            for j in range(self.maxSecond+1):
                degree = 0
                if self.validCoord(i,j+1) and not self.isWall(self.betterMap[i][j+1]):
                    degree = degree + 1
                if self.validCoord(i,j-1) and not self.isWall(self.betterMap[i][j-1]):
                    degree = degree + 1
                if self.validCoord(i-1,j) and not self.isWall(self.betterMap[i-1][j]):
                    degree = degree + 1
                if self.validCoord(i+1,j) and not self.isWall(self.betterMap[i+1][j]):
                    degree = degree + 1
                if degree > 2 or degree == 1:
                    self.junctions.append((i,j))
                    self.reverseJunctions[(i,j)] = len(self.junctions)-1 

        #Create adjacency matrix for junctions
        self.junctAdj = []
        for i in range(len(self.junctions)):
            self.junctAdj.append([])
            for j in range(len(self.junctions)):
                self.junctAdj[i].append(-1)

        for i in range(len(self.junctions)):
            x,y = self.junctions[i]
            #Expand Right
            canGo = self.validCoord(i+1,j) and not self.isWall(self.betterMap[i+1][j])
            if canGo:
                self.expandJunction(i,x,y,'R')
            #Expand Left
            canGo = self.validCoord(i-1,j) and not self.isWall(self.betterMap[i-1][j])
            if canGo:
                self.expandJunction(i,x,y,'L')
            #Expand Up
            canGo = self.validCoord(i,j-1) and not self.isWall(self.betterMap[i][j-1])
            if canGo:
                self.expandJunction(i,x,y,'U')
            #Expand Down
            canGo = self.validCoord(i,j+1) and not self.isWall(self.betterMap[i][j+1])
            if canGo:
                self.expandJunction(i,x,y,'D')
            

    def expandJunction(self,i,x,y,dir):
        '''Finds the neighbor of a junction'''
        pathLength = 0
        while canGo:
            pathLength = pathLength+1
            if dir=='R':
                x = x+1
                if (x,y) in self.junctions:
                    self.junctAdj[self.reverseJunctions[(x,y)]][i] = pathLength
                    break
                else:
                    if self.validCoord(i+1,j):
                        continue
                    elif self.validCoord(i,j-1):
                        dir = 'U'
                        continue
                    elif self.validCoord(i,j+1):
                        dir = 'D'
                        continue
            elif dir=='L':
                x = x-1
                if (x,y) in self.junctions:
                    self.junctAdj[self.reverseJunctions[(x,y)]][i] = pathLength
                    break
                else:
                    if self.validCoord(i-1,j):
                        continue
                    elif self.validCoord(i,j-1):
                        dir = 'U'
                        continue
                    elif self.validCoord(i,j+1):
                        dir = 'D'
                        continue
            elif dir=='U':
                y = y-1
                if (x,y) in self.junctions:
                    self.junctAdj[self.reverseJunction[(x,y)]][i] = pathLength
                    break
                else:
                    if self.validCoord(i,j-1):
                        continue
                    elif self.validCoord(i+1,j):
                        dir = 'R'
                        continue
                    elif self.validCoord(i-1,j):
                        dir = 'L'
                        continue
            elif dir=='D':
                y = y+1
                if (x,y) in self.junctions:
                    self.junctAdj[self.reverseJunction[(x,y)]][i] = pathLength
                    break
                else:
                    if self.validCoord(i,j+1):
                        continue
                    elif self.validCoord(i+1,j):
                        dir = 'R'
                        continue
                    elif self.validCoord(i-1,j):
                        dir = 'L'
                        continue

    def firstCoord(self, value):
        '''Takes an integer and returns the first coordinate in (row*maxCol) + col form'''
        return int(value / self.maxSecond)

    def secondCoord(self, value):
        '''Takes an integer and returns the second coordinate in (row*maxCol) + col form'''
        return (value % self.maxSecond)

    def validCoord(self, y, x):
        '''Returns if an (x,y) coordinate pair is valid'''
        return (x >= 0) and (y >= 0) and (x <= self.maxFirst) and (y <= self.maxSecond)

    def isWall(self, value):
        '''Returns true if the value corresponds to that of a wall tile'''
        return (100<=value<=199)

    def think(self, curMap, curPos, rivalPos, curGraceTime):
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
