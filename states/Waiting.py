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

import urllib.request, socket, web, State

class Waiting(State):
    # constructor
    def __init__(self, logger: Logger, crashOnHTTPError: bool, useTimer: int=0):
        super(logger, crashOnHTTPError, useTimer)

    # Set properties
    def setProperties(self):
        self.__stateCode = 0
        self.__stateName = "Waiting"


    # There aren't any errors to handle in this stage...
    def handleError(self):
        return 0