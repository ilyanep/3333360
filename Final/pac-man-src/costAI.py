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
        self.wasSuperman = False
        self.panic = False
                
    def think(self, curMap, selfStat, oppoStat, fruitPos, curGraceTime):
        #constants
        curPos = (int((selfStat[0][1]+8) / 16), int((selfStat[0][0]+8) / 16))
        self.curPos = curPos
        rivalPos = (int((oppoStat[0][1]+8) / 16), int((oppoStat[0][0]+8) / 16))
        self.rivalPos = rivalPos
        self.fruitPos = (int((fruitPos[1]+8) / 16), int((fruitPos[0]+8)/16))

        self.mySuperman = selfStat[1]
        self.myDigest = selfStat[2]
        self.myStun = selfStat[3]
        self.myScore = selfStat[4]

        self.rivalSuperman = oppoStat[1]
        self.rivalDigest = oppoStat[2]
        self.rivalStun = oppoStat[3]
        self.rivalScore = oppoStat[4]

        if self.panic == True:
            print "Panic mode is on"
        else:
            print "Panic mode is off"

        if self.rivalSuperman > 0 and self.ellOneNorm(curPos, rivalPos) < 5:
            self.panic = True

        if self.panic == True and (self.rivalSuperman == 0 or self.ellOneNorm(curPos, rivalPos) >= 8): 
            self.panic = False

        #If in between squares, we should probably not compute anything
        #TODO: Unless opponent has recently become super pacman
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
    #TODO: Factor in digestion times and opponent as super pacman and me as superpacman
    #into cost function
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
                    #newCost = cost + self.spaceCost(path, nextPoint, curMap, rivalPos)
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
        yf, xf = self.fruitPos
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
        if yf > 0 and xf > 0:
            fruitDist = 0
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
      
        pathScore = - expected frames to traverse + 16*number of dots picked up 

        returns (path, (yy, xx)) where path is a string of the characters {U,L,R,D}
        and (yy, xx) is the location of the dot described above.
        '''
        if self.mySuperman > 0:
            print "I am a superman"
            dotPenalty = 0
            framePenalty = 16
        elif self.mySuperman == 0:
            print "I am not a superman"
            dotPenalty = 5
            framePenalty = 16
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
                        newFrontier[(yy,xx+1)] = (v + 'R',p-framePenalty-dotPenalty+16)
                        foundDots.append((v + 'R', (yy, xx+1), p-framePenalty-dotPenalty+16))
                        foundPoints.append((yy,xx+1))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif right == 0 and not visited[yy][xx+1]:
                        visited[yy][xx+1] = 1
                        newFrontier[(yy,xx+1)] = (v + 'R',p-framePenalty)
                    elif right == 20 and not visited[yy][0]:
                        visited[yy][0] = 1
                        newFrontier[(yy,1)] = (v + 'R',p-framePenalty)
                if xx > 0:
                    left = curMap[(yy, xx-1)]
                    if left == 2 and (yy, xx-1) not in foundPoints:
                        visited[yy][xx-1] = 1
                        newFrontier[(yy,xx-1)] = (v+'L',p-framePenalty-dotPenalty+16)
                        foundDots.append((v + 'L', (yy, xx-1), p-framePenalty-dotPenalty+16))
                        foundPoints.append((yy,xx-1))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif left == 0 and not visited[yy][xx-1]:
                        visited[yy][xx-1] = 1
                        newFrontier[(yy, xx-1)] = (v + 'L', p-framePenalty)
                    elif left == 20 and not visited[yy][self.mapWidth-1]:
                        visited[yy][self.mapWidth-1] = 1
                        newFrontier[(yy, self.mapWidth-1)] = (v + 'L', p-framePenalty)
                if yy > 0:
                    up = curMap[(yy-1, xx)]
                    if up == 2 and (yy-1,xx) not in foundPoints:
                        visited[yy-1][xx] = 1
                        newFrontier[(yy-1,xx)] = (v + 'U', p-framePenalty-dotPenalty+16)
                        foundDots.append((v + 'U', (yy-1, xx), p-framePenalty-dotPenalty+16))
                        foundPoints.append((yy-1,xx))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif up == 0:
                        visited[yy-1][xx] = 1
                        newFrontier[(yy-1,xx)] = (v + 'U', p-framePenalty)
                    elif up == 21 and not visited[self.mapHeight-1][xx]:
                        visited[self.mapHeight-1][xx] = 1
                        newFrontier[(self.mapHeight-1,xx)] = (v + 'U', p-framePenalty)
                if yy < self.mapHeight - 1:
                    down = curMap[(yy+1,xx)]
                    if down == 2 and (yy+1,xx) not in foundPoints:
                        visited[yy+1][xx] = 1
                        newFrontier[(yy+1,xx)] = (v + 'D', p-framePenalty-dotPenalty+16)
                        foundDots.append((v + 'D', (yy+1,xx), p-framePenalty-dotPenalty+16))
                        foundPoints.append((yy+1,xx))
                        if len(foundDots) == numToFind:
                            return self.bestComponentDot(foundDots) #Process components
                    elif down == 0:
                        visited[yy+1][xx] = 1
                        newFrontier[(yy+1,xx)] = (v + 'D', p-framePenalty)
                    elif down == 21 and not visited[0][xx]:
                        visited[0][xx] = 1
                        newFrontier[(1, xx)] = (v + 'D', p-framePenalty)
            frontier = newFrontier
                
    def bestComponentDot(self, foundDots):
        '''Takes a set of dots, finds connected components, and returns the nearest dot in the best component'''
        if self.rivalSuperman > 0:
            print "Opponent is a superman"
            oppPenalty = 16
            fruitBonus = 0
        elif self.rivalSuperman == 0:
            print "Opponent is not a superman"
            oppPenalty = 0
            if self.fruitPos[0] > 0 and self.fruitPos[1] > 0:
                fruitBonus = 2
            else:
                fruitBonus = 0

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

        print components[i][leastOne[i]][1]

        compScore = [16*sizes[i] + components[i][leastOne[i]][2] + \
            oppPenalty*self.ellOneNorm(components[i][leastOne[i]][1], self.rivalPos) - 
            fruitBonus*self.ellOneNorm(components[i][leastOne[i]][1], self.fruitPos) for i in range(len(components))]

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

    def ellOneNorm(self, p1, p2):
        '''Returns the l1 norm of two points'''
        return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])

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
