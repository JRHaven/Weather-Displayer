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

class WrongURL(State):
    # constructor
    def __init__(self, logger: Logger, crashOnHTTPError: bool, useTimer: int=0):
        super(logger, crashOnHTTPError, useTimer)

    # Set properties
    def setProperties(self):
        self.__stateCode = 6
        self.__stateName = "Wrong URL or URL not accessible (HTTP 404 Error)"


    # Handle inability to get hourly weather JSON data
    def handleError(self, myName):
        self.__logger.log("STATE ", "HTTP 404 Error. Telling user and quitting...")
        system("clear")
        print("\nRecieved a 404 error. This likely means the url given \
in the url file is incorrect.\nRetry the process of finding the API URL and try again.")

        if(self.__useTimer == 1):
            self.__logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self.__logger.log("STATE ", "Quitting with exit value of 1!")
        return 1