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

from os import system
import urllib.request, socket, web, State

class TooManyErrors(State):
    # constructor
    def __init__(self, logger: Logger, crashOnHTTPError: bool, useTimer: int=0):
        super(logger, crashOnHTTPError, useTimer)

    # Set properties
    def setProperties(self):
        self.__stateCode = 9
        self.__stateName = "Too Many 500 Errors"


    # Handle inability to get hourly weather JSON data
    def handleError(self, myName):
        self.__logger.log("STATE ", "Excessive HTTP 500 errors. Telling the user and quitting...")
        system("clear")
        print("\nRecieved too many 500 errors. Usually these clear after a couple seconds,\n\
but not now. This is a NWS issue. Weather-Displayer cannot continue.\n\
Try again in a couple hours.")

        if(self.__useTimer == 1):
            self.__logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self.__logger.log("STATE ", "Quitting with exit value of 1!")
        return 1