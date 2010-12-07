import pygame, sys, os, random, math
from pygame.locals import *

class costAI2():
    def __init__(self, inputMap, curPos, rivalPos, mapHeight, mapWidth):
        s = ''
        for y in range(mapHeight):
            for x in range(mapWidth):
                s = s + str(inputMap[(y,x)]).center(4)
            s = s + '\n'
        f = open('dump.txt', 'w')
        f.write(s)
        f.close()
        self.mapHeight = mapHeight
        self.mapWidth = mapWidth
        self.curPath = ''
        
    def think(self, curMap, selfStat, oppoStat, fruitPos, curGraceTime):
    
        curPos = (int((selfStat[0][1]+8) / 16), int((selfStat[0][0]+8) / 16))
        self.curPos = curPos
        rivalPos = (int((oppoStat[0][1]+8) / 16), int((oppoStat[0][0]+8) / 16))
        self.rivalPos = rivalPos
        self.fruitPos = (int((fruitPos[1]+8) / 16), int((fruitPos[0]+8)/16))
        self.curMap = curMap;
                
        #If between squares then don't need to compute?
        if (selfStat[0][1]%16!=0) or (selfStat[0][0]%16!=0):
            #print 'corner'
            return self.curPath[0]
            
        self.curPath = self.dfsPath(curPos, 5, 0)
        print self.curPath + ' ' + str(self.pathCost(curPos, self.curPath)) + ' ' + str(self.pathCost(curPos, 'UULLD'))
        
        #self.curAction = random.choice("RUDL");
        #action = self.curPath[0]
        #self.curPath = self.curPath[1:]
        return self.curPath[0].upper()
        
    def dfsPath(self, start, length, dist):
        ''' start = (y, x) the starting point
            length = number of turns to look ahead
            dist = L1 distance from start of the path
            returns a string of actions
        '''
        y, x = start
        if length == 0:
            return ""
        paths = []
        if x > 0:
            left = self.curMap[(y, x-1)]
            if left == 0 or left == 2:
                paths.append('L' + self.dfsPath((y, x-1), length-1, dist+1))
            elif left == 20:
                paths.append('l' + self.dfsPath((y, self.mapWidth-1), length-1, dist+1) )
        if x < self.mapWidth - 1:
            right = self.curMap[(y, x+1)]
            if right == 0 or right == 2:
                paths.append('R' + self.dfsPath((y, x+1), length-1, dist+1))
            elif right == 20:
                paths.append('r' + self.dfsPath((y, 1), length-1, dist+1)) 
        if y > 0:
            up = self.curMap[(y-1, x)]
            if up == 0 or up == 2:
                paths.append('U' + self.dfsPath((y-1, x), length-1, dist+1) )
            elif up == 21:
                paths.append('u' + self.dfsPath((self.mapHeight-1, x), length-1, dist+1) )
        if y < self.mapHeight - 1:
            down = self.curMap[(y+1, x)]
            if down == 0 or down == 2:
                paths.append('D' + self.dfsPath((y+1, x), length-1, dist+1) )
            elif down == 21:
                paths.append('d' + self.dfsPath((1, x), length-1, dist+1) )
            
        bestPath = ''
        minCost = float('inf')
        for path in paths:
            cost = self.pathCost(start, path)
            #print path + ' ' + str(cost)
            if cost < minCost:
                minCost = cost
                bestPath = path
        return bestPath
        
    def move(self, pos, action):
        y, x = pos
        if action == 'L':
            x = x -1
        elif action == 'l':
            x = self.mapWidth-1
        elif action == 'R':
            x = x + 1
        elif action == 'r':
            x = 1
        elif action == 'U':
            y = y - 1
        elif action == 'u':
            y = self.mapHeight - 1
        elif action == 'D':
            y = y + 1
        elif action == 'd':
            y = 1
        return (y,x)
        
    def pathCost(self, start, path):
        ''' start = (y, x) is the starting point
            path = A string of actions
            returns cost of the path
        '''
        #print 'computing pathcost for ' + path
        y, x = start
        visited = [start]
        dist = 0
        cost = 0
        for action in path:
            if start == (4,2) and path == 'LLL':
                print action
            dist = dist + 1
            y, x = self.move((y,x), action)
            if start == (4,2) and path == 'LLL':
                print (y,x)
                print self.curMap[(y,x)]
            pellet = 0
            if (y,x) not in self.curMap:
                print 'start = ' + str(start)
                print 'path = ' + path
            if self.curMap[(y,x)] == 2 and not (y,x) in visited:
                pellet = 1
            cost = cost - 0.9 * dist * pellet * 10
            visited.append((y,x))
        return cost
    
    def ellOneNorm(self, p1, p2):
        '''Returns the l1 norm of two points'''
        return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])
                
            