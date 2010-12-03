import pygame, sys, os, random, math
from pygame.locals import *

class cheatyTimesAI ():
    def __init__(self, inputMap, curPos, rivalPos, mapHeight, mapWidth):
       None

    def think(self, curMap, curPos, rivalPos, curGraceTime):
        curMap[curPos] = 2
        return
