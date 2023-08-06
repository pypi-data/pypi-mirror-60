
import time
from Hospital import Hospital
from Person import State
import _thread
import pygame

class MyPanel:
    worldTime = 0
    def Run(self):
        while True:
            self.Paint()
            #time.sleep(0.1)
            MyPanel.worldTime += 1

    def __init__(self,screen:pygame.Surface):
        self.pIndex = 0
        screen.fill((68,68,68))#444444
        self.color:pygame.Color = None
        self.screen = screen
        self.s = State()
        _thread.start_new_thread(self.Run,())
    def Paint(self):
        self.screen.fill((68,68,68))
        '''
        self.t.pencolor('#00ff00')
        self.t.goto(Hospital.GetInstance().GetX(), Hospital.GetInstance().GetY())
        self.t.pendown()
        self.t.seth(90)
        self.t.forward(Hospital.GetInstance().GetWidth())
        self.t.seth(180)
        self.t.forward(Hospital.GetInstance().GetHeight())
        self.t.seth(270)
        self.t.forward(Hospital.GetInstance().GetWidth())
        self.t.seth(0)
        self.t.forward(Hospital.GetInstance().GetHeight())

        self.t.penup()
        '''
        from PersonPool import PersonPool
        people = PersonPool.GetInstance().GetPersonList()

        if people == None:
            return None
       
        people[self.pIndex].update()

        for person in people:
            if person.GetState() == self.s.NORMAL:
                self.color = pygame.Color('0xdddddd')
            elif person.GetState() == self.s.SHADOW:
                self.color = pygame.Color('0xffee00')
            elif person.GetState() == self.s.CONFIRMED or person.GetState() == self.s.FREEZE:
                self.color = pygame.Color('0xff0000')

            person.update()

            pygame.draw.circle(self.screen,self.color,(person.GetX(),person.GetY()),3)
        pygame.display.update()
        self.pIndex+=1
        if self.pIndex >= len(people):
            self.pIndex = 0

        