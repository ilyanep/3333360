import pygame, sys, os, random, math
from pygame.locals import *

class superGreedyAI():
    def __init__(self, inputMap, curPos, rivalPos):
        self.path = ""
        self.mapHeight = 0
        self.mapWidth = 0
        self.target = (0,0)
        for k,v in inputMap.iteritems():
            y, x = k
            if y > self.mapHeight:
                self.mapHeight = y
            if x > self.mapWidth:
                self.mapWidth = x
            if v == 20:
                print '20 is the value of ', k
            elif v == 21:
                print '21 is the value of ', k
        
    def think(self, curMap, curPos, rivalPos, curGraceTime):
        y, x = curPos
        dotDirs = []
        openDirs = []
        right = curMap[(y, x+1)]
        left = curMap[(y, x-1)]
        up = curMap[(y-1, x)]
        down = curMap[(y+1, x)]
        if right==2:
            dotDirs.append('R')
            
        if left==2:
            dotDirs.append('L')
            
        if down==2:
            dotDirs.append('D')
            
        if up==2:
            dotDirs.append('U')
            
        if len(dotDirs) > 0:
            if len(self.path) == 0:
                self.path, self.target = self.dottyPath(x, y, 15, curMap)
            print 'Dotty path is ', self.path
            move = self.path[0]
            self.path = self.path[1:]
            return move
        else:
            if len(self.path) == 0 or curMap[self.target] == 0:
                self.path, self.target = self.nearestDot(x, y, curMap)
            print 'Path to dot is ', self.path
            move = self.path[0]
            self.path = self.path[1:]
            return move
           
        # visited = [[0 for i in range(self.mapWidth)] for j in range(self.mapHeight)]
            
    def dottyPath(self, x, y, length, curMap):
        bestPath = ""
        target = (y,x)
        frontier = [((y,x),'')]
        visited = [(y,x)]
        lastlen = 0
        while len(bestPath) < length and len(frontier) > 0:
            point, path = frontier.pop()
            if len(path) < lastlen:
                visited.pop()
                lastlen = len(path)
            visited.append(point)
            yy, xx = point
            if xx < self.mapWidth and (yy,xx+1) not in visited:
                right = curMap[(yy,xx+1)]
                if right == 2:
                    frontier.append( ((yy,xx+1), path + 'R') )
                    if len(path) >= len(bestPath):
                        bestPath = path + 'R'
                        target = (yy, xx+1)
            if xx > 0 and (yy,xx-1) not in visited:
                left = curMap[(yy,xx-1)]
                if left == 2:
                    frontier.append( ((yy,xx-1), path + 'L') )
                    if len(path) >= len(bestPath):
                        bestPath = path + 'L'
                        target = (yy, xx-1)
            if yy < self.mapHeight and (yy+1,xx) not in visited:
                down = curMap[(yy+1, xx)]
                if down == 2:
                    frontier.append( ((yy+1,xx), path + 'D') )
                    if len(path) >= len(bestPath):
                        bestPath = path + 'D'
                        target = (yy+1, xx)
            if yy > 0 and (yy-1, xx) not in visited:
                up = curMap[(yy-1, xx)]
                if up == 2:
                    frontier.append( ((yy-1, xx), path + 'U') )
                    if len(path) >= len(bestPath):
                        bestPath = path + 'U'
                        target = (yy-1, xx)
        return (bestPath, target)

        
    def nearestDot(self, x, y, curMap):
        '''Finds the path from (y,x) to the nearest dot using BFS; 
        
        returns (path, (yy, xx)) where path is a string of the characters {U,L,R,D}
        and (yy, xx) is the location of the nearest dot.
        '''
        frontier = {(y,x) : ""}
        visited = [[0 for i in range(self.mapWidth)] for j in range(self.mapHeight)]
        while(1):
            newFrontier = {};
            for k,v in frontier.iteritems():
                yy, xx = k
                if xx < self.mapWidth:
                    right = curMap[(yy, xx+1)]
                    if right == 2:
                        return (v + 'R', (yy, xx+1))
                    elif right == 0 and not visited[yy][xx+1]:
                        visited[yy][xx+1] = 1
                        newFrontier[(yy,xx+1)] = v + 'R'
                    elif right == 20 and not visited[yy][0]:
                        visited[yy][0] = 1
                        newFrontier[(yy,0)] = v + 'R'
                if xx > 0:
                    left = curMap[(yy, xx-1)]
                    if left == 2:
                        return (v + 'L', (yy, xx-1))
                    elif left == 0 and not visited[yy][xx-1]:
                        visited[yy][xx-1] = 1
                        newFrontier[(yy, xx-1)] = v + 'L'
                    elif left == 20 and not visited[yy][self.mapWidth-1]:
                        visited[yy][self.mapWidth-1] = 1
                        newFrontier[(yy, self.mapWidth-1)] = v + 'L'
                if yy > 0:
                    up = curMap[(yy-1, xx)]
                    if up == 2:
                        return (v + 'U', (yy-1, xx))
                    elif up == 0:
                        visited[yy-1][xx] = 1
                        newFrontier[(yy-1,xx)] = v + 'U'
                    elif up == 21 and not visited[self.mapHeight-1][xx]:
                        visited[self.mapHeight-1][xx] = 1
                        newFrontier[(self.mapHeight-1,xx)] = v + 'U'
                if yy < self.mapHeight:
                    down = curMap[(yy+1,xx)]
                    if down == 2:
                        return (v + 'D', (yy+1,xx))
                    elif down == 0:
                        visited[yy+1][xx] = 1
                        newFrontier[(yy+1,xx)] = v + 'D'
                    elif down == 21 and not visited[0][xx]:
                        visited[0][xx] = 1
                        newFrontier[(0, xx)] = v + 'D'
            frontier = newFrontier
                
                
                
                
                
                