import pygame, sys, os, random, math
from pygame.locals import *

class superGreedyAI():
    def __init__(self, inputMap, curPos, rivalPos):
        None
        
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
        elif right==0:
            openDirs.append('R')
        if left==2:
            dotDirs.append('L')
        elif left==0:
            openDirs.append('L')
        if down==2:
            dotDirs.append('D')
        elif down==0:
            openDirs.append('D')
        if up==2:
            dotDirs.append('U')
        elif up==0:
            openDirs.append('U')
        if len(dotDirs) > 0:
            return random.choice(dotDirs)
        else:
            return random.choice(openDirs)