'''
This file is part of Weather-Displayer.

Weather-Displayer is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the Free 
Software Foundation, either version 3 of the License, or (at your option) any 
later version.

Weather-Displayer is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
details.

You should have received a copy of the GNU General Public License along with 
Weather-Displayer. If not, see <https://www.gnu.org/licenses/>. 
'''

# Base Getter Class that will be expanded for different states

from abc import ABC, abstractmethod
from Model import Model
from Logger import Logger
import urllib.request, socket

class State(ABC):
    __logger = None

    # constructor
    def __init__(self, model: Model, logger: Logger):
        self._model = model
        self._logger = logger

        self.setProperties()

    # We'll compare states using state codes.
    @abstractmethod
    def setProperties(self):
        pass

    # Other getters and setters when necessary
    def getCode(self) -> int:
        return self._stateCode


    # What to do on error
    @abstractmethod
    def handleError(self):
        return None


    # Magic methods
    def __eq__(self, otherState: object):
        return self._stateCode == otherState.getCode()
    
    def __str__(self):
        return self._stateName
    
    def __repr__(self):
        return str(self._stateCode) + ":" + self.__stateName
    
    def __int__(self):
        return self._stateCode