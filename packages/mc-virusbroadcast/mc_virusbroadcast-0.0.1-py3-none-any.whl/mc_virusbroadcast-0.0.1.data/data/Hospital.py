from Constants import Constants
from Point import Point
from Bed import Bed
import sys
sys.setrecursionlimit(5000)
class Hospital:
    __hospital = None
    def __init__(self):
        
        self.__x = 800
        self.__y = 110
        
        self.__height = 606

        if Constants.BED_COUNT == 0:
            self.__width = 0
            self.__height = 0
        self.column = Constants.BED_COUNT//100;
        self.__width = self.column * 6
        #__hospital:Hospital = Hospital()
        self.__point = Point(800,100)
        self.__beds = []
        if self.column < 1:
            self.column = 1
        self.n = 0
        for i in range(self.column):
            for j in range(10, 611, 6):
                if self.n > Constants.BED_COUNT:
                    break
                bed = Bed(self.__point.GetX() + i * 6, self.__point.GetY() + j)
                self.__beds.append(bed)
                self.n += 1
                
        

    def GetWidth(self):
        return self.__width

    def GetHeight(self):
        return self.__height

    def GetX(self):
        return self.__x
    def GetY(self):
        return self.__y

    
    def GetInstance():
        if Hospital.__hospital == None:
            Hospital.__hospital = Hospital()
        return Hospital.__hospital
    

    def PickBed(self):
        for self.bed in self.__beds:
            if self.bed.IsEmpty():
                return self.bed

        return None
Hospital()