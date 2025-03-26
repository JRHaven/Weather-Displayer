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

from Logger import Logger
import os

# Make all configs in a central model object
class Model:
    __tweaks = {}

    # Constructor calls other method to load items from .weatherdisprc
    def __init__(self, logger):
        self.__logger = logger
        self.__tweaksFromFile()

    # Get tweaks from .weatherdisprc
    def __tweaksFromFile(self):
        with open(".weatherdisprc", "r") as config:
            # Take out trailing whitespace, and then loop
            for i in config.read().strip().split("\n"):
                if(i == ""):
                    continue
                if(i[0] == "#"):
                    continue

                element = i.split("=")
                try:
                    self.__tweaks[element[0].strip()] = int(element[1].strip())
                except ValueError:
                    self.__logger.log("MODEL ", "ERROR: Cannot convert to int! Skipping, with dummy value of 0.")
                    self.__tweaks[element[0]] = 0
            config.close()

        # Convert to properties for easy handling in client code
        self.__propertiesFromTweaks()
    
    def __propertiesFromTweaks(self):
        # Shouldn't assume .weatherdisprc hasn't been tampered; check for existance
        # and assign default values if they don't
        if("web-server" in self.__tweaks):
            self.__webInterface = bool(self.__tweaks["web-server"])
        if("show-IP" in self.__tweaks):
            self.__showIP = bool(self.__tweaks["show-IP"])
        if("time" in self.__tweaks):
            self.__useClock = self.__tweaks["time"]
        if("stop-on-http-error" in self.__tweaks):
            self.__crashOnHTTPError = bool(self.__tweaks["stop-on-http-error"])
        if("close-timer" in self.__tweaks):
            self.__useTimer = bool(self.__tweaks["stop-on-http-error"])
        if("ip-network" in self.__tweaks):
            self.__ipNet = self.__tweaks["ip-network"]
        if("port" in self.__tweaks):
            self.__srvPort = self.__tweaks["port"]

    # Properties for getters. Attributes are and should be read-only.
    @property
    def webInterface(self) -> bool:
        return self.__webInterface
    
    @property
    def showIP(self) -> bool:
        return self.__showIP
    
    @property
    def useClock(self) -> int:
        return self.__useClock
    
    @property
    def crashOnHTTPError(self) -> bool:
        return self.__crashOnHTTPError
    
    @property
    def useTimer(self) -> bool:
        return self.__useTimer
    
    @property
    def ipNet(self) -> int:
        return self.__ipNet
    
    @property
    def srvPort(self) -> bool:
        return self.__srvPort
    
    @property
    def tweaks(self) -> dict:
        return self.__tweaks