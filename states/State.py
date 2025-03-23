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

import urllib.request, socket, web

class State:
    __logger = None

    # Configurables from .weatherdisprc
    __crashError = True
    __useTimer = 0

    # State properties that will be changed by extended states
    __stateCode = -1
    __stateName = ""

    # constructor
    def __init__(self, stateStack: tuple):
        self.__crashError = stateStack[1]
        self.__logger = stateStack[0]

        # Handle no timer given
        if(len(stateStack) > 2):
            self.__useTimer = stateStack[2]
        else:
            self.useTimer = 0

        self.setProperties()

    # We'll compare states using state codes.
    @abstractmethod
    def setProperties(self):
        pass

    # Other getters and setters when necessary
    def getCode(self) -> int:
        return self.__stateCode


    # What to do on error
    @abstractmethod
    def handleError(self):
        return None


    # Magic methods
    def __eq__(self, otherState: object):
        return self.__stateCode == otherState.getCode()
    
    def __str__(self):
        return self.__stateName
    
    def __repr__(self):
        return str(self.__stateCode) + ":" + self.__stateName
    
    def __int__(self):
        return tself.__stateCode