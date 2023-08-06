'''
这是病毒模拟器
包含简单的病毒传播试验
请注意！
这不是演习！
'''
import Main
from Constants import *
from Virus import Virus
import pygame
import sys
from PersonPool import PersonPool
from Person import Person
from MyPanel import MyPanel
import _thread

screen:pygame.Surface = None
def Init(title:str):
    '''
    初始化窗口
        Args:
            title:窗口标题
    '''
    if type(title) != str:
        print('标题请输入字符串')
        sys.exit()
    global screen
    screen = Main.Init(title)

def CreateVirus():
    '''
    创建病毒
        return:所创建的病毒
    '''
    if screen == None:
        print('未初始化窗口，程序退出')
        sys.exit()
    return Virus(screen)

p = None
people = None
def Start():
    '''
    开始模拟
    '''
    global p
    p = MyPanel(screen)
    global people
    people = PersonPool.GetInstance().GetPersonList()

    _thread.start_new_thread(Main.test,(people,))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
    pass
def CreateCity():
    '''
    创建一个城市
        return:所创建的城市
    '''
    return City()
def CreateHospital():
    '''
    创建一所医院
        return:所创建的医院
    '''
    return Hospital()

class City:
    '''
    这应该是一座城市
    '''
    def __init__(self):
        pass
    def SetAllPersonCount(self, ALL_PERSON_COUNT:int = 100):
        """
        此方法用于设置城市总人口数
            Args:
                ALL_PERSON_NUMBER:总人口数(1 - 350)
        """
        if type(ALL_PERSON_COUNT) != int:
            print("数值类型不符")
            return None
        if ALL_PERSON_COUNT<=0 or ALL_PERSON_COUNT>350:
            print("设置的数值超出范围（1 - 350）")
            return None
        Constants.ALL_PERSON_NUMBER = ALL_PERSON_COUNT

class Hospital:
    '''
    唯一的一所医院，宇宙终极无敌豪华版
    '''
    def __init__(self):
        pass
    def SetBedCount(self, BED_COUNT:int = 10):
        """
        此方法用于设置医院床位
            Args:
                BED_COUNT:医院床位(1 - 350)
        """
        if type(BED_COUNT) != int:
            print("数值类型不符")
            return None
        if BED_COUNT<=0 or BED_COUNT>350:
            print("设置的数值超出范围（1 - 350）")
            return None
        Constants.BED_COUNT = BED_COUNT


    def SetHospitalReceiveTime(self, HOSPITAL_RECEIVE_TIME:int = 10):
        """
        此方法用于设置院收治响应时间
            Args:
                HOSPITAL_RECEIVE_TIME:院收治响应时间(1 - 1000)
        """
        if type(HOSPITAL_RECEIVE_TIME) != int:
            print("数值类型不符")
            return None
        if HOSPITAL_RECEIVE_TIME<=0 or HOSPITAL_RECEIVE_TIME>1000:
            print("设置的数值超出范围（1 - 1000）")
            return None
        Constants.HOSPITAL_RECEIVE_TIME = HOSPITAL_RECEIVE_TIME

