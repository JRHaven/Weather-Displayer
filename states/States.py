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

# All the states in one file for easy importation

from os import system
from states.State import State
from Logger import Logger
from time import sleep

class WrongURL(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 6
        self.__stateName = "Wrong URL or URL not accessible (HTTP 404 Error)"


    # Handle inability to get hourly weather JSON data
    def handleError(self):
        self._logger.log("STATE ", "HTTP 404 Error. Telling user and quitting...")
        system("clear")
        print("\nRecieved a 404 error. This likely means the url given \
in the url file is incorrect.\nRetry the process of finding the API URL and try again.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1

class NewJSON(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 5
        self.__stateName = "New JSON Retrieved"


    # There is no error
    def handleError(self):
        return None


class Waiting(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 0
        self.__stateName = "Waiting"


    # There aren't any errors to handle in this stage...
    def handleError(self):
        return None


class NoHourJSON(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 3
        self.__stateName = "No hourly JSON data"


    # Handle inability to get hourly weather JSON data
    def handleError(self):
        self._logger.log("STATE ", "Couldn't get hourly weather JSON. Prompting user to quit...")
        system("clear")
        print("\nERROR: Could not retrieve hourly weather data.\nWeather-Displayer cannot continue.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1


class NoBackups(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 8
        self.__stateName = "No Backups"


    # Handle inability to get hourly weather JSON data
    def handleError(self):
        self._logger.log("STATE ", "No backups, when backups were required. Telling the user and quitting...")
        system("clear")
        print("\nWas unable to acquire needed backups to sort out an error.\nWeather-Displayer cannot continue.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1


class JSONWrongURL(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 10
        self.__stateName = "json.decoder.JSONDecodeError - Wrong URL"


    # Handle inability to get hourly weather JSON data
    def handleError(self):
        self._logger.log("STATE ", "JSON decode error - probably wrong url. Telling the user and quitting...")
        system("clear")
        print("\nEncountered JSON decode error. This is likely the\nresult of an incorrect url.\n\
Retry the process of finding the API URL and try again.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1


class OutDateJSON(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 4
        self.__stateName = "Provided JSON out of date"


    # Handle situation when JSON is out of date
    def handleError(self):
        self._logger.log("STATE ", "JSON data was out of date, as such that nothing could be displayed.")
        system("cowsay -d \"Inaccurate Data\"")

        # WAIT!!!! for getter to continue going
        sleep(300)
        
        return None


class ServerError(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 7
        self.__stateName = "HTTP 503 Error"


    # Handle inability to get hourly weather JSON data
    def handleError(self):
        self._logger.log("STATE ", "HTTP 503 error. Telling the user and quitting...")
        system("clear")
        print("\nRecieved a 503 error. This is an error on the NWS end, usually\n\
meaning the server down, possibly under maintenance.\n\
Weather-Displayer cannot continue. Try again in a few hours.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1


class TooManyErrors(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 9
        self.__stateName = "Too Many 500 Errors"


    # Handle inability to get hourly weather JSON data
    def handleError(self):
        self._logger.log("STATE ", "Excessive HTTP 500 errors. Telling the user and quitting...")
        system("clear")
        print("\nRecieved too many 500 errors. Usually these clear after a couple seconds,\n\
but not now. This is a NWS issue. Weather-Displayer cannot continue.\n\
Try again in a couple hours.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1


class NoGenJSON(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 2
        self.__stateName = "No general JSON data"


    # Handle inability to get general weather JSON data
    def handleError(self):
        self._logger.log("STATE ", "Couldn't get general weather JSON. Prompting user to quit...")
        system("clear")
        print("\nERROR: Could not retrieve general weather data.\nWeather-Displayer cannot continue.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1


class NoURL(State):
    # Set properties
    def setProperties(self):
        self._stateCode = 1
        self.__stateName = "No URL File"


    # Handle no URL file error
    def handleError(self):
        self._logger.log("STATE ", "No URL Found! Prompting user to quit...")
        system("clear")
        print("\nERROR: Could not find the NWS Destination URL!\n\
If this is your first time running the script, you may have not\nput in the \
destination URL. If you don't know how to do this,\ngo to https://github.com/JRHaven/Weather-Displayer\n\
and read the README.md file to explain the steps to do this.")

        if(self._model.useTimer == True):
            self._logger.log("STATE ", "Configured to quit automatically. Will close in 60 seconds.")
            sleep(60)
        else:
            input("Press enter to exit...")
        
        self._logger.log("STATE ", "Quitting with exit value of 1!")
        return 1