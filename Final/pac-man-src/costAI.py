import pygame, sys, os, random, math
from pygame.locals import *

class costAI():
    def __init__(self, inputMap, curPos, rivalPos, mapHeight, mapWidth):
        self.path = ""
        self.mapHeight = mapHeight
        self.mapWidth = mapWidth
        self.target = (0,0)
        self.oldpath = ""
        self.curAction = "U"
                
    def think(self, curMap, selfStat, oppoStat, fruitPos, curGraceTime):

        #constants
        curPos = (int((selfStat[0][1]+8) / 16), int((selfStat[0][0]+8) / 16))
        rivalPos = (int((oppoStat[0][1]+8) / 16), int((oppoStat[0][0]+8) / 16))

        mySuperman = selfStat[1]
        myDigest = selfStat[2]
        myStun = selfStat[3]
        myScore = selfStat[4]
        
        rivalSuperman = oppoStat[1]
        rivalDigest = oppoStat[2]
        rivalStun = oppoStat[3]
        rivalScore = oppoStat[4]

        #If in between squares, we should probably not compute anything
        if (selfStat[0][1]%16!=0) | (selfStat[0][0]%16!=0):
            return self.curAction

        #Actual code
        y, x = curPos
        path = self.minCostPath(curPos, 7, curMap, rivalPos)
        print "Min cost path: ",path
        if len(path) > 0:
            self.oldpath = ""
        if len(path) == 0:
            if len(self.oldpath) > 0 and curMap[self.target] == 2:
                print "Using cached path: ", self.oldpath
                path = self.oldpath
            else:
                path, self.target, pathScore = self.nearestDot(x, y, curMap,10)
                print "Using new path: ", path
            self.oldpath = path[1:]
        self.curAction = path[0] 
        return path[0]
        
    def minCostPath(self, start, length, curMap, rivalPos):
        frontier = [(([start], "", 0))]
        for i in range(length):
            if len(frontier) == 0:
                break
            newFrontier = [];
            for elem in frontier:
                path, strPath, cost = elem
                y, x = path[-1]
                nextPoints = []
                if x > 0:
                    left = curMap[(y, x-1)]
                    if left == 0 or left == 2:
                        nextPoints.append(['L',(y,x-1)])
                    elif left == 20:
                        nextPoints.append(['L',(y, self.mapWidth-1)])
                if x < self.mapWidth - 1:
                    right = curMap[(y, x+1)]
                    if right == 0 or right == 2:
                        nextPoints.append(['R',(y, x+1)])
                    elif right == 20:
                        nextPoints.append(['R',(y, 1)])
                if y > 0:
                    up = curMap[(y-1, x)]
                    if up == 0 or up == 2:
                        nextPoints.append(['U',(y-1,x)])
                    elif up == 21:
                        nextPoints.append(['U',(self.mapHeight-1,x)])
                if y < self.mapHeight - 1:
                    down = curMap[(y+1,x)]
                    if down == 0 or down == 2:
                        nextPoints.append(['D',(y+1,x)])
                    elif down == 21:
                        nextPoints.append(['D', (1, x)])
                    
                for elem2 in nextPoints:
                    nextDir, nextPoint = elem2
                    newPath = path + [nextPoint]
                    newCost = cost + cost + self.spaceCost(path, nextPoint, curMap, rivalPos)
                    newStrPath = strPath + nextDir
                    newFrontier.append((newPath, newStrPath, newCost))
            frontier = newFrontier
        minCost = 10
        bestPath = ""
        for elem in frontier:
            path, strPath, cost = elem
            if cost < minCost:
                bestPath = strPath
                minCost = cost
        return bestPath        
                
    def spaceCost(self, path, point, curMap, rivalPos):
        y0, x0 = path[0]
        y1, x1 = point
        yr, xr = rivalPos
        length = len(path)
        dist = abs(x0-x1) + abs(y0-y1)
        pellet = 0
        visited = 0
        if point in path:
            visited = 1
        if curMap[point] == 2:
            pellet = 1
        cost = dist
        if pellet and not visited:
            cost = cost - 10
        if yr-length < y1 < yr+length and xr-length < x1 < xr+length:
            cost = cost + 100 / (length*length)
        return cost
        
        
        
        
    def numDots(self, curMap):
        num = 0
        for yy in range(self.mapHeight):
            for xx in range(self.mapWidth):
                if curMap[(yy,xx)] == 2:
                    num = num+1
        return num
        
    def nearestDot(self, x, y, curMap, numToFind):
        '''Finds the path from (y,x) to the nearest dot that is within the best cluster
        when the nearest numToFind dots are considered. Best cluster is determined
        by clusterScore = size(cluster) + pathScore of nearest element 

        pathScore = - distance + number of pellets along the path
        
        returns (path, (yy, xx)) where path is a string of the characters {U,L,R,D}
        and (yy, xx) is the location of the dot described above.
        '''
        frontier = {(y,x) : ("",0)}
        maxDots = self.numDots(curMap)
        numToFind = min(maxDots, numToFind) #Guarantee this many dots are on the board
        foundDots = []
        foundPoints = []
        visited = [[0 for i in range(self.mapWidth+1)] for j in range(self.mapHeight+1)]
        while(1):
            newFrontier = {}
            for k,m in frontier.iteritems():
                v = m[0]
                p = m[1]
                yy, xx = k
                if xx < self.mapWidth - 1:
                    right = curMap[(yy, xx+1)]
                    if right == 2 and (yy,xx+1) not in foundPoints:
                        visited[yy][xx+1] = 1
                        newFrontier[(yy,xx+1)] = (v + 'R',p)
                        foundDots.append((v + 'R', (yy, xx+1), p))
                        foundPoints.append((yy,xx+1))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif right == 0 and not visited[yy][xx+1]:
                        visited[yy][xx+1] = 1
                        newFrontier[(yy,xx+1)] = (v + 'R',p-1)
                    elif right == 20 and not visited[yy][0]:
                        visited[yy][0] = 1
                        newFrontier[(yy,1)] = (v + 'R',p-1)
                if xx > 0:
                    left = curMap[(yy, xx-1)]
                    if left == 2 and (yy, xx-1) not in foundPoints:
                        visited[yy][xx-1] = 1
                        newFrontier[(yy,xx-1)] = (v+'L',p)
                        foundDots.append((v + 'L', (yy, xx-1), p))
                        foundPoints.append((yy,xx-1))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif left == 0 and not visited[yy][xx-1]:
                        visited[yy][xx-1] = 1
                        newFrontier[(yy, xx-1)] = (v + 'L', p-1)
                    elif left == 20 and not visited[yy][self.mapWidth-1]:
                        visited[yy][self.mapWidth-1] = 1
                        newFrontier[(yy, self.mapWidth-1)] = (v + 'L', p-1)
                if yy > 0:
                    up = curMap[(yy-1, xx)]
                    if up == 2 and (yy-1,xx) not in foundPoints:
                        visited[yy-1][xx] = 1
                        newFrontier[(yy-1,xx)] = (v + 'U', p)
                        foundDots.append((v + 'U', (yy-1, xx), p))
                        foundPoints.append((yy-1,xx))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif up == 0:
                        visited[yy-1][xx] = 1
                        newFrontier[(yy-1,xx)] = (v + 'U', p-1)
                    elif up == 21 and not visited[self.mapHeight-1][xx]:
                        visited[self.mapHeight-1][xx] = 1
                        newFrontier[(self.mapHeight-1,xx)] = (v + 'U', p-1)
                if yy < self.mapHeight - 1:
                    down = curMap[(yy+1,xx)]
                    if down == 2 and (yy+1,xx) not in foundPoints:
                        visited[yy+1][xx] = 1
                        newFrontier[(yy+1,xx)] = (v + 'D', p)
                        foundDots.append((v + 'D', (yy+1,xx), p))
                        foundPoints.append((yy+1,xx))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif down == 0:
                        visited[yy+1][xx] = 1
                        newFrontier[(yy+1,xx)] = (v + 'D', p-1)
                    elif down == 21 and not visited[0][xx]:
                        visited[0][xx] = 1
                        newFrontier[(1, xx)] = (v + 'D', p-1)
            frontier = newFrontier
                
    def bestComponentDot(self, foundDots):
        '''Takes a set of dots, finds connected components, and returns the nearest dot in the best component'''
        visited = [[0 for i in range(self.mapWidth+1)] for j in range(self.mapHeight+1)]
        components = []
        adjacentDots = {} 

        #Build adjacency list
        for i in range(len(foundDots)):
            adjacentDots[foundDots[i][1]] = []
            for j in range(len(foundDots)):
                if self.isNeighbor(foundDots[i][1], foundDots[j][1]):
                    adjacentDots[foundDots[i][1]].append(foundDots[j])

        #Build components
        for i in range(len(foundDots)):
            if visited[foundDots[i][1][0]][foundDots[i][1][1]]:
                continue
            visited[foundDots[i][1][0]][foundDots[i][1][1]] = 1
            components.append([foundDots[i]])
            stack = []
            stack.extend(adjacentDots[foundDots[i][1]])
            while len(stack)>0:
                curEl = stack.pop()
                if visited[curEl[1][0]][curEl[1][1]]:
                    continue
                visited[curEl[1][0]][curEl[1][1]] = 1
                stack.extend(adjacentDots[curEl[1]])
                components[len(components)-1].append(curEl)

        #Find least dist within each component
        leastOne = []
        for i in range(len(components)):
            leastDist = (self.mapWidth+1) * (self.mapHeight+1)
            whichOne = -1
            for j in range(len(components[i])):
                if len(components[i][j][0]) < leastDist:
                    leastDist = len(components[i][j][0])
                    whichOne = j
            leastOne.append(whichOne)

        #Find size of components
        sizes = [len(components[i]) for i in range(len(components))]

        compScore = [sizes[i] + components[i][leastOne[i]][2] for i in range(len(components))]

        maxscore = -(self.mapWidth * self.mapHeight * self.mapWidth * self.mapHeight)
        which = -1
        for i in range(len(components)):
            if compScore[i] > maxscore:
                maxscore = compScore[i]
                which = i
        whichOne = leastOne[which]


        print "Components are, ", components
        print "Chose,", which

        return components[which][whichOne]

    def isNeighbor(self, point1, point2):
        '''Takes two points and returns if they are neighbors'''
        yy1, xx1 = point1
        yy2, xx2 = point2

        if (yy2 == yy1-1) and (xx1 == xx2):
            return True
        if (yy2 == yy1+1) and (xx1 == xx2):
            return True
        if (xx1 == xx2-1) and (yy1 == yy2):
            return True
        if (xx1 == xx2+1) and (yy1 == yy2):
            return True
