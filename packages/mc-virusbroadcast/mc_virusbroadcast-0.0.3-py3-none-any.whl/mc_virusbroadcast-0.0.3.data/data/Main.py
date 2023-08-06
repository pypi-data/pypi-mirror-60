from MyPanel import MyPanel
import _thread
import time
from PersonPool import PersonPool
from Person import Person
from Constants import Constants
import random
import pygame
import sys


def Init(title:'新冠状病毒模拟'):
    pygame.init()
    screen = pygame.display.set_mode(size = (1000,800),flags = pygame.DOUBLEBUF|pygame.RESIZABLE);
    pygame.display.set_caption(title)
    return screen



def test(people):
    for i in range(Constants.ORIGINAL_COUNT):
        index = random.randint(0, len(people)-1)
        person = people[index]

        while person.IsInfected():
            index = random.randint(0, len(people)-1)
            person = people[index]

        person.beInfected()


    
    #screen.fill((68,68,68))
   

