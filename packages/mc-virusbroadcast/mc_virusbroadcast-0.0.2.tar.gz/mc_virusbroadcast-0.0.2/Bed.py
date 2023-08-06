from Point import Point
class Bed(Point):
    def __init__(self, x:int, y:int):
        Point.__init__(self, x, y)
        self.__isEmpty = True

    def IsEmpty(self):
        return self.__isEmpty

    def SetEmpty(self, empty:bool):
        self.__isEmpty = empty

    


