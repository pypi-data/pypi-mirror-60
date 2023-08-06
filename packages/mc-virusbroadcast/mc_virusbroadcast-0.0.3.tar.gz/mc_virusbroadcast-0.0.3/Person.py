from City import City
from MoveTarget import MoveTarget
import random
from Constants import Constants

from Hospital import Hospital
from Bed import Bed
import math
import numpy.matlib
import numpy as np
import time

class State:
    def __init__(self):
        self.NORMAL = 0;
        self.SUSPECTED = self.NORMAL+1;
        self.SHADOW = self.SUSPECTED+1;

        self.CONFIRMED = self.SHADOW+1;
        self.FREEZE = self.CONFIRMED+1;
        self.CURED = self.FREEZE+1;

class Person:
    gb = True

    def __init__(self, city:City, x:int, y:int):
        self.__city = city
        self.__x = x
        self.__y = y
        self.__targetSig = 50
        self.__targetXU = 100 * numpy.random.normal() + x
        self.__targetYU = 100 * numpy.random.normal() + y
        self.__moveTarget:MoveTarget = None
        self.__sig = 1
        self.city:City = None
        self.s = State()
        self.__state = self.s.NORMAL
        self.__infectedTime = 0
        self.__confirmedTime = 0
        self.__SAFE_DIST = 2.0
        
    def wantMove(self):
        value = self.__sig * numpy.random.normal() + Constants.u
        return value > 0
    
    

    def GetState(self):
        return self.__state

    def SetState(self, state:State):
        if state == self.s.NORMAL:
            self.__state = self.s.NORMAL
        elif state == self.s.CONFIRMED:
            self.__state = self.s.CONFIRMED
        elif state == self.s.CURED:
            self.__state = self.s.CURED
        elif state == self.s.FREEZE:
            self.__state = self.s.FREEZE
        elif state == self.s.SHADOW:
            self.__state = self.s.SHADOW
        elif state == self.s.SUSPECTED:
            self.__state = self.s.SUSPECTED

    def GetX(self):
        return self.__x
    def SetX(self, x:int):
        self.__x = x;
    def GetY(self):
        return self.__y
    def SetY(self, y:int):
        self.__y = y;

    

    def IsInfected(self):
        return self.__state >= self.s.SHADOW

    def beInfected(self):
        self.__state = self.s.SHADOW
        from MyPanel import MyPanel
        self.__infectedTime = MyPanel.worldTime

    def distance(self, person):
        return math.sqrt(math.pow(self.__x - person.GetX(), 2) + math.pow(self.__y - person.GetY(),2))

    def Freezy(self):
        self.__state = self.s.FREEZE

    def MoveTo(self, x:int, y:int):
        self.__x += x
        self.__y += y

    def Action(self):
        if self.__state == self.s.FREEZE:
            return None
        if not self.wantMove():
            return None
        if self.__moveTarget == None or self.__moveTarget.IsArrived():
            targetX = self.__targetSig * numpy.random.normal() + self.__targetXU
            targetY = self.__targetSig * numpy.random.normal() + self.__targetYU
            self.__moveTarget = MoveTarget(int(targetX),int(targetY))
        dx = self.__moveTarget.GetX() - self.__x
        dy = self.__moveTarget.GetY() - self.__y
        length = math.sqrt(math.pow(dx,2) + math.pow(dy,2))

        if length < 1:
            self.__moveTarget.SetArrived(True)
            return None
        udx = int(dx/length)
        if udx == 0 and dx != 0:
            if dx > 0:
                udx = 1
            else:
                udx = -1
        udy = int(dy/length)
        if udy == 0 and udy != 0:
            if dy > 0:
                udy = 1
            else:
                uny = -1
        
        if self.__x > 700:
            self.__moveTarget = None
            if udx > 0:
                udx = -udx

        self.MoveTo(udx, udy)

    

    def update(self):
        from MyPanel import MyPanel
        if self.__state >= self.s.FREEZE:
            return None
        if self.__state == self.s.CONFIRMED and MyPanel.worldTime - self.__confirmedTime >= Constants.HOSPITAL_RECEIVE_TIME:
            bed = Hospital.GetInstance().PickBed()
            if bed == None:
                if Person.gb:
                    print('隔离区没有空床位')
                    Person.gb = False
                
            else:
                self.__state = self.s.FREEZE
                self.__x = bed.GetX()
                self.__y = bed.GetY()
                bed.SetEmpty(False)
        if MyPanel.worldTime - self.__infectedTime > Constants.SHADOW_TIME and self.__state == self.s.SHADOW:
            self.__state = self.s.CONFIRMED
            self.__confirmedTime = MyPanel.worldTime

        self.Action()
        from PersonPool import PersonPool
        people = PersonPool.GetInstance().GetPersonList()

        if self.__state >= self.s.SHADOW:
            return None

        for p in people:
            if p.GetState() == self.s.NORMAL:
                continue
            r = random.uniform(-1.0, 1.0)

            if r < Constants.BED_COUNT and self.distance(p) < self.__SAFE_DIST:
                self.beInfected()
