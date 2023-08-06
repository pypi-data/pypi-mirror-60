from Constants import *
import pygame
class Virus:
    '''
    这是一个病毒?
    '''
    def __init__(self,screen:pygame.Surface):
        self.screen = screen
        pass

    def SetShadowTime(self, SHADOW_TIME:int = 140):
        """
        此方法用于设置病毒潜伏时间
            Args:
                SHADOW_TIME:病毒潜伏时间(1 - 1000)
        """
        if type(SHADOW_TIME) != int:
            print("数值类型不符")
            return None
        if SHADOW_TIME<=0 or SHADOW_TIME>1000:
            print("设置的数值超出范围（1 - 1000）")
            return None
        Constants.SHADOW_TIME = SHADOW_TIME


    def SetOrigunalCount(self, ORIGINAL_COUNT:int = 20):
        """
        此方法用于设置初始感染数量
            Args:
                ORIGINAL_COUNT:初始感染数量(1 - 350)
        """
        if type(ORIGINAL_COUNT) != int:
            print("数值类型不符")
            return None
        if ORIGINAL_COUNT<=0 or ORIGINAL_COUNT>350:
            print("设置的数值超出范围（1 - 350）")
            return None
        Constants.ORIGINAL_COUNT = ORIGINAL_COUNT


    def SetBroadRate(self, BROAD_RATE:int = 80):
        """
        此方法用于设置传播率
            Args:
                BROAD_RATE::传播率(1 - 100)(百分比)
        """
        if type(BROAD_RATE) != int:
            print("BROAD_RATE")
            return None
        if BROAD_RATE<=0 or BROAD_RATE>100:
            print("设置的数值超出范围（1 - 100）")
            return None
        Constants.BROAD_RATE = BROAD_RATE//100