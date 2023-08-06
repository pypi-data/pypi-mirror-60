class MoveTarget:
    

    def __init__(self, x:int, y:int):
        self.__x = x
        self.__y = y
        self.__arrived = False;

    def GetX(self):
        return self.__x
    def SetX(self, x:int):
        self.__x = x

    def GetY(self):
        return self.__y
    def SetX(self, y:int):
        self.__y = y

    def IsArrived(self):
        return self.__arrived
    def SetArrived(self, arrived:bool):
        self.__arrived = arrived

