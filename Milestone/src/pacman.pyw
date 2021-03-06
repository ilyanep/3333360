#! /usr/bin/python

# pacman.pyw
# By David Reilly

# Modified by Andy Sommerville, 8 October 2007:
# - Changed hard-coded DOS paths to os.path calls
# - Added constant SCRIPT_PATH (so you don't need to have pacman.pyw and res in your cwd, as long
# -   as those two are in the same directory)
# - Changed text-file reading to accomodate any known EOLn method (\n, \r, or \r\n)
# - I (happily) don't have a Windows box to test this. Blocks marked "WIN???"
# -   should be examined if this doesn't run in Windows
# - Added joystick support (configure by changing JS_* constants)
# - Added a high-score list. Depends on wx for querying the user's name

import pygame, sys, os, random, math
import threeSixty, doNothing, randomWalk, superGreedy, costAI, cheatyTimes
from pygame.locals import *
#team1AI = superGreedy.superGreedyAI
team1AI = costAI.costAI
team2AI = superGreedy.superGreedyAI
#team2AI = cheatyTimes.cheatyTimesAI
#team2AI = randomWalk.randomWalkAI
#team2AI = doNothing.doNothingAI
#team2AI = costAI.costAI

# WIN???
SCRIPT_PATH = sys.path[0]

# NO_GIF_TILES -- tile numbers which do not correspond to a GIF file
# currently only "23" for the high-score list
NO_GIF_TILES = [23]

# Joystick defaults - maybe add a Preferences dialog in the future?
JS_DEVNUM = 0 # device 0 (pygame joysticks always start at 0). if JS_DEVNUM is not a valid device, will use 0
JS_XAXIS = 0 # axis 0 for left/right (default for most joysticks)
JS_YAXIS = 1 # axis 1 for up/down (default for most joysticks)
JS_STARTBUTTON = 0 # button number to start the game. this is a matter of personal preference, and will vary from device to device

clock = pygame.time.Clock()
pygame.init()

window = pygame.display.set_mode((1, 1))
pygame.display.set_caption("PacMan CS154")

screen = pygame.display.get_surface()

img_Background = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "backgrounds", "1.gif")).convert()

pygame.mixer.init()

snd_pellet = {}
snd_pellet[0] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "res", "sounds", "pellet1.wav"))
snd_pellet[1] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "res", "sounds", "pellet2.wav"))



#CS154 PARAMS
MILESTONE_MAP_NO = 1
TEAM_NAMES = ["Team-1", "Team-2"]

#     _____________________
# ___/  class definitions  \_______________________________________________

class game ():

    def defaulthiscorelist(self):
            return []
            
    def getplayername(self):
            return USER_NAME
            
    def __init__ (self):
        self.score = [0,0]
        # game "mode" variable
        # 1 = normal
        # 2 = hit ghost
        # 3 = game over
        # 4 = wait to start
        # 5 = wait after eating ghost
        # 6 = wait after finishing level
        self.mode = 0
        self.modeTimer = 0
        
        self.SetMode(3)
        
        # camera variables
        self.screenPixelPos = (0, 0) # absolute x,y position of the screen from the upper-left corner of the level
        self.screenNearestTilePos = (0, 0) # nearest-tile position of the screen from the UL corner
        self.screenPixelOffset = (0, 0) # offset in pixels of the screen from its nearest-tile position
        
        self.screenTileSize = (25, 21)
        self.screenSize = (self.screenTileSize[1] * 16, self.screenTileSize[0] * 16)

        # numerical display digits
        self.digit = {}
        for i in range(0, 10, 1):
            self.digit[i] = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "text", str(i) + ".gif")).convert()
        self.imLife = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "text", "life.gif")).convert()
        self.imGameOver = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "text", "gameover.gif")).convert()
        self.imReady = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "text", "ready.gif")).convert()
        self.imLogo = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "text", "logo.gif")).convert()
        #self.imHiscores = self.makehiscorelist()
        
    def StartNewGame (self):
        self.score = [0,0]
        self.SetMode(4)
        thisLevel.LoadLevel(MILESTONE_MAP_NO)
            
    def AddToScore (self, amount, teamID):
        self.score[teamID] += amount
        
    
    def DrawScore (self):
        self.DrawNumber (self.score[0], (24 + 16, self.screenSize[1] - 36))
        self.DrawNumber (self.score[1], (24 + 16, self.screenSize[1] - 24))
            
        if self.mode == 3:
            screen.blit (self.imGameOver, (self.screenSize[0] / 2 - 32, self.screenSize[1] / 2 - 10))
        elif self.mode == 4:
            screen.blit (self.imReady, (self.screenSize[0] / 2 - 20, self.screenSize[1] / 2 + 12))
            
    def DrawNumber (self, number, x_y):
        x, y = x_y
        strNumber = str(int(number))
        
        for i in range(0, len(strNumber), 1):
            iDigit = int(strNumber[i])
            screen.blit (self.digit[ iDigit ], (x + i * 9, y))
        
      
    def MoveScreen (self, newX_newY):
        newX, newY = newX_newY
        self.screenPixelPos = (newX, newY)
        self.screenNearestTilePos = (int(newY / 16), int(newX / 16)) # nearest-tile position of the screen from the UL corner
        self.screenPixelOffset = (newX - self.screenNearestTilePos[1] * 16, newY - self.screenNearestTilePos[0] * 16)
        
    def GetScreenPos (self):
        return self.screenPixelPos
        
        
    def SetMode (self, newMode):
        self.mode = newMode
        self.modeTimer = 0
        # print " ***** GAME MODE IS NOW ***** " + str(newMode)
        

class pacman ():
    
    def __init__ (self, newID):
        self.teamID = newID
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 2
        
        self.nearestRow = 0
        self.nearestCol = 0
        
        self.homeX = 0
        self.homeY = 0
        
        self.anim_pacmanL = {}
        self.anim_pacmanR = {}
        self.anim_pacmanU = {}
        self.anim_pacmanD = {}
        self.anim_pacmanS = {}
        self.anim_pacmanCurrent = {}
        
        self.graceTime = 0
        
        self.curAction = 'U'
        
        
        for i in range(1, 9, 1):
            self.anim_pacmanL[i] = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "sprite", "pacman-l " + str(i) + '-' + str(newID+1) + ".gif")).convert()
            self.anim_pacmanR[i] = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "sprite", "pacman-r " + str(i) + '-' + str(newID+1) + ".gif")).convert()
            self.anim_pacmanU[i] = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "sprite", "pacman-u " + str(i) + '-' + str(newID+1) + ".gif")).convert()
            self.anim_pacmanD[i] = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "sprite", "pacman-d " + str(i) + '-' + str(newID+1) + ".gif")).convert()
            self.anim_pacmanS[i] = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "sprite", "pacman" + '-' + str(newID+1) + ".gif")).convert()

        self.pelletSndNum = 0
        
    def Move (self):
        self.nearestRow = int(((self.y + 8) / 16))
        self.nearestCol = int(((self.x + 8) / 16))

        if ((self.y%16)==0 and (self.x%16)==0):
            startTime = pygame.time.get_ticks()
            if self.teamID == 0:
                self.curAction = team1.think(thisLevel.map, (self.nearestRow, self.nearestCol), (player[1].nearestRow, player[1].nearestCol), self.graceTime)
            else:
                self.curAction = team2.think(thisLevel.map, (self.nearestRow, self.nearestCol), (player[0].nearestRow, player[0].nearestCol), self.graceTime)
                
            endTime = pygame.time.get_ticks()
            self.executeAction(self.curAction)
            
            if (endTime-startTime>100):
                self.graceTime += endTime-startTime-100
                print "Player " + str(self.teamID+1) + " used " + str(endTime-startTime-100) + " ms grace time!"
            if self.graceTime>5000:
                print "Player " + str(self.teamID+1) + " timeout!"
                thisGame.SetMode(7)
            

        # make sure the current velocity will not cause a collision before moving
        if not thisLevel.CheckIfHitWall((self.x + self.velX, self.y + self.velY), (self.nearestRow, self.nearestCol)):

            # check for collisions with other tiles (pellets, etc)
            thisLevel.CheckIfHitDoor((self.x, self.y), self.teamID, (self.nearestRow, self.nearestCol))
            
            # it's ok to Move
            self.x += self.velX
            self.y += self.velY
            
            thisLevel.CheckIfHitPellet()
            

            

        
        else:
            # we're going to hit a wall -- stop moving
            self.velX = 0
            self.velY = 0
            
                
            
        
    def Draw (self):
        
        if thisGame.mode == 3:
            return False
        
        # set the current frame array to match the direction pacman is facing
        if self.velX > 0:
            self.anim_pacmanCurrent = self.anim_pacmanR
        elif self.velX < 0:
            self.anim_pacmanCurrent = self.anim_pacmanL
        elif self.velY > 0:
            self.anim_pacmanCurrent = self.anim_pacmanD
        elif self.velY < 0:
            self.anim_pacmanCurrent = self.anim_pacmanU
            
        screen.blit (self.anim_pacmanCurrent[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
        
        if thisGame.mode == 1:
            if not self.velX == 0 or not self.velY == 0:
                # only Move mouth when pacman is moving
                self.animFrame += 1 
            
            if self.animFrame == 9:
                # wrap to beginning
                self.animFrame = 1
                

    def executeAction(self, curChoice):
        if curChoice == 'R':
            self.velX = self.speed
            self.velY = 0
        elif curChoice == 'L':
            self.velX = -self.speed
            self.velY = 0
        elif curChoice == 'D':
            self.velY = self.speed
            self.velX = 0
        elif curChoice == 'U':
            self.velY = -self.speed
            self.velX = 0
        elif curChoice == 'H':
            self.velX = 0
            self.velY = 0



class level ():
    
    def __init__ (self):
        self.lvlWidth = 0
        self.lvlHeight = 0
        self.edgeLightColor = (255, 255, 0, 255)
        self.edgeShadowColor = (255, 150, 0, 255)
        self.fillColor = (0, 255, 255, 255)
        self.pelletColor = (255, 255, 255, 255)
        
        self.map = {}
        self.pellets = 0

    def GetMapTile (self, row_col):
        row, col = row_col
        if row >= 0 and row < self.lvlHeight and col >= 0 and col < self.lvlWidth:
            return self.map[row, col]
        else:
            return 0
    
    def IsWall (self, row, col):
    
        if row > thisLevel.lvlHeight - 1 or row < 0:
            return True
        
        if col > thisLevel.lvlWidth - 1 or col < 0:
            return True
    
        # check the offending tile ID
        result = thisLevel.GetMapTile((row, col))

        # if the tile was a wall
        if result >= 100 and result <= 199:
            return True
        else:
            return False
    
                    
    def CheckIfHitWall (self, possiblePlayerX_possiblePlayerY, row_col):
        row, col = row_col
        possiblePlayerX, possiblePlayerY = possiblePlayerX_possiblePlayerY
        numCollisions = 0
        
        # check each of the 9 surrounding tiles for a collision
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):
            
                if  (math.fabs(possiblePlayerX - (iCol * 16)) < 16) and (math.fabs(possiblePlayerY - (iRow * 16)) < 16):
                    
                    if self.IsWall(iRow, iCol):
                        numCollisions += 1
                        
        if numCollisions > 0:
            return True
        else:
            return False
        
        
    def CheckIfHit (self, playerX_playerY, x_y, cushion):
        x, y = x_y
        playerX, playerY = playerX_playerY
    
        if (math.fabs(playerX - x) < cushion) and (math.fabs(playerY - y) < cushion):
            return True
        else:
            return False


    def CheckIfHitDoor (self, playerX_playerY, playerID, row_col):
        row, col = row_col        
        playerX, playerY = playerX_playerY
    
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):
                if  (math.fabs(playerX - (iCol * 16)) < 8) and (math.fabs(playerY - (iRow * 16)) < 8):
                    # check the offending tile ID
                    result = thisLevel.GetMapTile((iRow, iCol))
                    if result == tileID[ 'door-h' ]:
                        if player[playerID].velX > 0:
                            player[playerID].x -= (thisLevel.lvlWidth-2)*16;
                        else:
                            player[playerID].x += (thisLevel.lvlWidth-2)*16;
                                        
                    elif result == tileID[ 'door-v' ]:
                        # ran into a vertical door
                        if player[playerID].velY > 0:
                            player[playerID].y -= (thisLevel.lvlHeight-2)*16;
                        else:
                            player[playerID].y += (thisLevel.lvlHeight-2)*16;

    
    def CheckIfHitPellet (self):
        
        for curID in range(0, 2):
            col = player[curID].nearestCol
            row = player[curID].nearestRow
            
            curX = player[curID].x
            curY = player[curID].y
            oppoX = player[1-curID].x
            oppoY = player[1-curID].y
            
            for iRow in range(row - 1, row + 2, 1):
                for iCol in range(col - 1, col + 2, 1):
                    if  (math.fabs(curX - iCol*16) < 4) and (math.fabs(curY - iRow*16) < 4):
                        # check the offending tile ID
                        result = thisLevel.GetMapTile((iRow, iCol))
            
                        if result == tileID[ 'pellet' ]:
                            thisLevel.map[iRow, iCol] = 0
                            thisLevel.pellets -= 1
                            if (math.fabs(oppoX - iCol*16) < 8) and (math.fabs(oppoY - iRow*16) < 8):
                                snd_pellet[player[curID].pelletSndNum].play()
                                snd_pellet[player[1-curID].pelletSndNum].play()
                                player[curID].pelletSndNum = 1 - player[curID].pelletSndNum
                                player[1-curID].pelletSndNum = 1 - player[1-curID].pelletSndNum
                                thisGame.AddToScore(5, curID)
                                thisGame.AddToScore(5, 1-curID)
                            else:
                                snd_pellet[player[curID].pelletSndNum].play()
                                player[curID].pelletSndNum = 1 - player[curID].pelletSndNum
                                thisGame.AddToScore(10, curID)
                            
                            if thisLevel.pellets == 0:
                                # no more pellets left!
                                # WON THE LEVEL
                                thisGame.SetMode(6)

                                        
    def GetPathwayPairPos (self):
        
        doorArray = []
        
        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile((row, col)) == tileID[ 'door-h' ]:
                    # found a horizontal door
                    doorArray.append((row, col))
                elif self.GetMapTile((row, col)) == tileID[ 'door-v' ]:
                    # found a vertical door
                    doorArray.append((row, col))
        
        if len(doorArray) == 0:
            return False
        
        chosenDoor = random.randint(0, len(doorArray) - 1)
        
        if self.GetMapTile(doorArray[chosenDoor]) == tileID[ 'door-h' ]:
            # horizontal door was chosen
            # look for the opposite one
            for i in range(0, thisLevel.lvlWidth, 1):
                if not i == doorArray[chosenDoor][1]:
                    if thisLevel.GetMapTile((doorArray[chosenDoor][0], i)) == tileID[ 'door-h' ]:
                        return doorArray[chosenDoor], (doorArray[chosenDoor][0], i)
        else:
            # vertical door was chosen
            # look for the opposite one
            for i in range(0, thisLevel.lvlHeight, 1):
                if not i == doorArray[chosenDoor][0]:
                    if thisLevel.GetMapTile((i, doorArray[chosenDoor][1])) == tileID[ 'door-v' ]:
                        return doorArray[chosenDoor], (i, doorArray[chosenDoor][1])
                    
        return False
        
    def PrintMap (self):
        
        for row in range(0, self.lvlHeight, 1):
            outputLine = ""
            for col in range(0, self.lvlWidth, 1):
            
                outputLine += str(self.map[row, col]) + ", "
                
            print outputLine
            
    def DrawMap (self):
        
        for row in range(-1, thisGame.screenTileSize[0] + 1, 1):
            outputLine = ""
            for col in range(-1, thisGame.screenTileSize[1] + 1, 1):

                # row containing tile that actually goes here
                actualRow = thisGame.screenNearestTilePos[0] + row
                actualCol = thisGame.screenNearestTilePos[1] + col

                useTile = self.GetMapTile((actualRow, actualCol))
                if not useTile == 0 and not useTile == tileID['door-h'] and not useTile == tileID['door-v']:
                    # if this isn't a blank tile

                    if useTile == tileID['pellet-power']:
                        if self.powerPelletBlinkTimer < 30:
                            screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]))

                    elif useTile == tileID['showlogo']:
                        screen.blit (thisGame.imLogo, (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]))
                    
                    elif useTile == tileID['hiscores']:
                            screen.blit(thisGame.imHiscores, (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]))
                    
                    else:
                        screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]))
        
    def LoadLevel (self, levelNum):
        
        self.map = {}
        
        self.pellets = 0
        
        f = open(os.path.join(SCRIPT_PATH, "res", "levels", str(levelNum) + ".txt"), 'r')
        lineNum = -1
        rowNum = 0
        useLine = False
        isReadingLevelData = False
          
        for line in f:

          lineNum += 1
        
            # print " ------- Level Line " + str(lineNum) + " -------- "
          while len(line) > 0 and (line[-1] == "\n" or line[-1] == "\r"): line = line[:-1]
          while len(line) > 0 and (line[0] == "\n" or line[0] == "\r"): line = line[1:]
          str_splitBySpace = line.split(' ')
            
            
          j = str_splitBySpace[0]
                
          if (j == "'" or j == ""):
                # comment / whitespace line
                # print " ignoring comment line.. "
                useLine = False
          elif j == "#":
                # special divider / attribute line
                useLine = False
                
                firstWord = str_splitBySpace[1]
                
                if firstWord == "lvlwidth":
                    self.lvlWidth = int(str_splitBySpace[2])
                    # print "Width is " + str( self.lvlWidth )
                    
                elif firstWord == "lvlheight":
                    self.lvlHeight = int(str_splitBySpace[2])
                    # print "Height is " + str( self.lvlHeight )
                    
                elif firstWord == "edgecolor":
                    # edge color keyword for backwards compatibility (single edge color) mazes
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeLightColor = (red, green, blue, 255)
                    self.edgeShadowColor = (red, green, blue, 255)
                    
                elif firstWord == "edgelightcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeLightColor = (red, green, blue, 255)
                    
                elif firstWord == "edgeshadowcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeShadowColor = (red, green, blue, 255)
                
                elif firstWord == "fillcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.fillColor = (red, green, blue, 255)
                    
                elif firstWord == "pelletcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.pelletColor = (red, green, blue, 255)
                    

                elif firstWord == "startleveldata":
                    isReadingLevelData = True
                        # print "Level data has begun"
                    rowNum = 0
                    
                elif firstWord == "endleveldata":
                    isReadingLevelData = False
                    # print "Level data has ended"
                    
          else:
                useLine = True
                
                
            # this is a map data line   
          if useLine == True:
                
                if isReadingLevelData == True:
                        
                    # print str( len(str_splitBySpace) ) + " tiles in this column"
                    
                    for k in range(self.lvlWidth):
                        self.map[rowNum, k] = int(str_splitBySpace[k])
                        
                        thisID = int(str_splitBySpace[k])
                        if thisID == 4: 
                            # starting position for pac-man 1                            
                            player[0].homeX = k * 16
                            player[0].homeY = rowNum * 16
                            self.map[rowNum, k] = 0
                        elif thisID == 5:
                            # starting position for pac-man 2
                            player[1].homeX = k * 16
                            player[1].homeY = rowNum * 16
                            self.map[rowNum, k] = 0
                        elif thisID == 2:
                            # pellet                            
                            self.pellets += 1
                            
                    rowNum += 1
                    
                
        # reload all tiles and set appropriate colors
        GetCrossRef()


        
        # do all the level-starting stuff
        self.Restart()
        
    def Restart (self):
            


        for playerID in range(2):
            player[playerID].x = player[playerID].homeX
            player[playerID].y = player[playerID].homeY
            player[playerID].nearestCol = int(player[playerID].x/16)
            player[playerID].nearestRow = int(player[playerID].y/16)
            player[playerID].velX = 0
            player[playerID].velY = 0       
            player[playerID].anim_pacmanCurrent = player[playerID].anim_pacmanS
            player[playerID].animFrame = 3


def CheckIfCloseButton(events):
    for event in events: 
        if event.type == QUIT: 
            thisGame.SetMode(6)


def CheckInputs(): 
    
    if thisGame.mode == 1:
        if pygame.key.get_pressed()[ pygame.K_d ]:
            if not thisLevel.CheckIfHitWall((player[0].x + player[0].speed, player[0].y), (player[0].nearestRow, player[0].nearestCol)): 
                player[0].velX = player[0].speed
                player[0].velY = 0
                
        elif pygame.key.get_pressed()[ pygame.K_a ]:
            if not thisLevel.CheckIfHitWall((player[0].x - player[0].speed, player[0].y), (player[0].nearestRow, player[0].nearestCol)): 
                player[0].velX = -player[0].speed
                player[0].velY = 0
            
        elif pygame.key.get_pressed()[ pygame.K_s ]:
            if not thisLevel.CheckIfHitWall((player[0].x, player[0].y + player[0].speed), (player[0].nearestRow, player[0].nearestCol)): 
                player[0].velX = 0
                player[0].velY = player[0].speed
            
        elif pygame.key.get_pressed()[ pygame.K_w ]:
            if not thisLevel.CheckIfHitWall((player[0].x, player[0].y - player[0].speed), (player[0].nearestRow, player[0].nearestCol)):
                player[0].velX = 0
                player[0].velY = -player[0].speed
                
        
        if pygame.key.get_pressed()[ pygame.K_RIGHT ]:
            if not thisLevel.CheckIfHitWall((player[1].x + player[1].speed, player[1].y), (player[1].nearestRow, player[1].nearestCol)): 
                player[1].velX = player[1].speed
                player[1].velY = 0
                
        elif pygame.key.get_pressed()[ pygame.K_LEFT ]:
            if not thisLevel.CheckIfHitWall((player[1].x - player[1].speed, player[1].y), (player[1].nearestRow, player[1].nearestCol)): 
                player[1].velX = -player[1].speed
                player[1].velY = 0
            
        elif pygame.key.get_pressed()[ pygame.K_DOWN ]:
            if not thisLevel.CheckIfHitWall((player[1].x, player[1].y + player[1].speed), (player[1].nearestRow, player[1].nearestCol)): 
                player[1].velX = 0
                player[1].velY = player[1].speed
            
        elif pygame.key.get_pressed()[ pygame.K_UP ]:
            if not thisLevel.CheckIfHitWall((player[1].x, player[1].y - player[1].speed), (player[1].nearestRow, player[1].nearestCol)):
                player[1].velX = 0
                player[1].velY = -player[1].speed
                
    if pygame.key.get_pressed()[ pygame.K_ESCAPE ]:
        thisGame.SetMode(6)
            
    elif thisGame.mode == 3:
        if pygame.key.get_pressed()[ pygame.K_RETURN ]:
            thisGame.StartNewGame()
            

    
#      _____________________________________________
# ___/  function: Get ID-Tilename Cross References  \______________________________________ 
    
def GetCrossRef ():

    f = open(os.path.join(SCRIPT_PATH, "res", "crossref.txt"), 'r')
    # ANDY -- edit
    #fileOutput = f.read()
    #str_splitByLine = fileOutput.split('\n')

    lineNum = 0
    useLine = False

    for i in f.readlines():
        # print " ========= Line " + str(lineNum) + " ============ "
        while len(i) > 0 and (i[-1] == '\n' or i[-1] == '\r'): i = i[:-1]
        while len(i) > 0 and (i[0] == '\n' or i[0] == '\r'): i = i[1:]
        str_splitBySpace = i.split(' ')
        
        j = str_splitBySpace[0]
            
        if (j == "'" or j == "" or j == "#"):
            # comment / whitespace line
            # print " ignoring comment line.. "
            useLine = False
        else:
            # print str(wordNum) + ". " + j
            useLine = True
        
        if useLine == True:
            tileIDName[ int(str_splitBySpace[0]) ] = str_splitBySpace[1]
            tileID[ str_splitBySpace[1] ] = int(str_splitBySpace[0])
            
            thisID = int(str_splitBySpace[0])
            if not thisID in NO_GIF_TILES:
                tileIDImage[ thisID ] = pygame.image.load(os.path.join(SCRIPT_PATH, "res", "tiles", str_splitBySpace[1] + ".gif")).convert()
            else:
                    tileIDImage[ thisID ] = pygame.Surface((16, 16))
            
            # change colors in tileIDImage to match maze colors
            for y in range(0, 16, 1):
                for x in range(0, 16, 1):
                
                    if tileIDImage[ thisID ].get_at((x, y)) == (255, 206, 255, 255):
                        # wall edge
                        tileIDImage[ thisID ].set_at((x, y), thisLevel.edgeLightColor)
                        
                    elif tileIDImage[ thisID ].get_at((x, y)) == (132, 0, 132, 255):
                        # wall fill
                        tileIDImage[ thisID ].set_at((x, y), thisLevel.fillColor) 
                        
                    elif tileIDImage[ thisID ].get_at((x, y)) == (255, 0, 255, 255):
                        # pellet color
                        tileIDImage[ thisID ].set_at((x, y), thisLevel.edgeShadowColor)   
                        
                    elif tileIDImage[ thisID ].get_at((x, y)) == (128, 0, 128, 255):
                        # pellet color
                        tileIDImage[ thisID ].set_at((x, y), thisLevel.pelletColor)   
                
            # print str_splitBySpace[0] + " is married to " + str_splitBySpace[1]
        lineNum += 1


#      __________________
# ___/  main code block  \_____________________________________________________

# create the pac-man
player = [pacman(0), pacman(1)]

tileIDName = {} # gives tile name (when the ID# is known)
tileID = {} # gives tile ID (when the name is known)
tileIDImage = {} # gives tile image (when the ID# is known)


# create game and level objects and load first level
thisGame = game()
thisLevel = level()
thisLevel.LoadLevel(MILESTONE_MAP_NO)


team1 = team1AI(thisLevel.map, (player[0].nearestRow, player[0].nearestCol), (player[1].nearestRow, player[1].nearestCol), thisLevel.lvlHeight, thisLevel.lvlWidth)
team2 = team2AI(thisLevel.map, (player[1].nearestRow, player[1].nearestCol), (player[0].nearestRow, player[0].nearestCol), thisLevel.lvlHeight, thisLevel.lvlWidth)

#print (thisGame.screenSize)
window = pygame.display.set_mode(thisGame.screenSize, pygame.DOUBLEBUF | pygame.HWSURFACE)

js = None

while True: 

    CheckIfCloseButton(pygame.event.get())
    
   
    if thisGame.mode == 1:
        # normal gameplay mode
        CheckInputs()
        
        thisGame.modeTimer += 1
        player[0].Move()
        player[1].Move()

            
               
    elif thisGame.mode == 3:
        # game over
        CheckInputs()
            
    elif thisGame.mode == 4:
        # waiting to start
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 30:
            thisGame.SetMode(1)
            player[0].velX = player[0].speed
            player[1].velX = player[1].speed
            
    elif thisGame.mode == 5:
        # brief pause after munching a vulnerable ghost
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 30:
            thisGame.SetMode(1)
            
    elif thisGame.mode == 6:
        # pause after eating all the pellets
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 30:
            thisGame.SetMode(7)
            oldEdgeLightColor = thisLevel.edgeLightColor
            oldEdgeShadowColor = thisLevel.edgeShadowColor
            oldFillColor = thisLevel.fillColor

            
    elif thisGame.mode == 7:

        # flashing maze after finishing level
        thisGame.modeTimer += 1
        
        whiteSet = [10, 30, 50, 70]
        normalSet = [20, 40, 60, 80]
        
        if not whiteSet.count(thisGame.modeTimer) == 0:
            # member of white set
            thisLevel.edgeLightColor = (255, 255, 255, 255)
            thisLevel.edgeShadowColor = (255, 255, 255, 255)
            thisLevel.fillColor = (0, 0, 0, 255)
            GetCrossRef()
        elif not normalSet.count(thisGame.modeTimer) == 0:
            # member of normal set
            thisLevel.edgeLightColor = oldEdgeLightColor
            thisLevel.edgeShadowColor = oldEdgeShadowColor
            thisLevel.fillColor = oldFillColor
            GetCrossRef()
        elif thisGame.modeTimer == 150:
            print TEAM_NAMES[0]+' score: '+str(thisGame.score[0])+"     Grace time: "+str(player[0].graceTime)
            print TEAM_NAMES[1]+' score: '+str(thisGame.score[1])+"     Grace time: "+str(player[1].graceTime)
            sys.exit(0)
            
    
    screen.blit(img_Background, (0, 0))
    
    if not thisGame.mode == 8:
        thisLevel.DrawMap()


        player[0].Draw()
        player[1].Draw()
        
        
    
    thisGame.DrawScore()
    
    pygame.display.flip()
    
    clock.tick (40)

