
from City import City
import random
import sys
import numpy.matlib
import numpy as np
import Constants
sys.setrecursionlimit(5000)
class PersonPool():
    pepersonPool = None

    def GetInstance():
        if PersonPool.pepersonPool == None:
            PersonPool.pepersonPool = PersonPool()
        return PersonPool.pepersonPool
    def __init__(self):
        self.personList = []
        
        city = City(400, 400)
        for i in range(Constants.Constants.ALL_PERSON_NUMBER):
            x = int(100 * numpy.random.normal() + city.GetCenterX())
            y = int(100 * numpy.random.normal() + city.GetCenterY())
            if x > 700:
                x = 700
            from Person import Person
            person = Person(city, x, y)
            self.personList.append(person)

    def GetPersonList(self): 
        return self.personList
PersonPool()