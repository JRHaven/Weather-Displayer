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
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__tweaksFromFile()

    # Get tweaks from .weatherdisprc
    def __tweaksFromFile(self):
        # If the config file doesn't exist, initialize!
        self.__logger.log("MODEL ", "Loading configurations...")
        if(not os.path.exists(".weatherdisprc")):
            logger.log(myName, ".weatherdisprc doesn't exist! Initializing...")
            self.__initConfig()
        
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
        else:
            self.__logger("MODEL ", "web-server not in config! Continuing with default value (false)")
            self.__webInterface = False
        
        # Tell logger about webInterface
        logger.setRunSrv(webInterface)
        
        if("show-IP" in self.__tweaks):
            self.__showIP = bool(self.__tweaks["show-IP"])
        else:
            self.__logger("MODEL ", "show-IP not in config! Continuing with default value (false)")
            self.__showIP = False
        
        if("time" in self.__tweaks):
            self.__useClock = self.__tweaks["time"]
        else:
            self.__logger("MODEL ", "time not in config! Continuing with default value (0)")
            self.__useClock = 0
        
        if("stop-on-http-error" in self.__tweaks):
            self.__crashOnHTTPError = bool(self.__tweaks["stop-on-http-error"])
        else:
            self.__logger("MODEL ", "stop-on-http-error not in config! Continuing with default value (true)")
            self.__crashOnHTTPError = True
        
        if("close-timer" in self.__tweaks):
            self.__useTimer = bool(self.__tweaks["stop-on-http-error"])
        else:
            self.__logger("MODEL ", "close-timer not in config! Continuing with default value (false)")
            self.__useTimer = False
        
        if("ip-network" in self.__tweaks):
            self.__ipNet = self.__tweaks["ip-network"]
        else:
            self.__logger("MODEL ", "ip-network not in config! Continuing with default value (10)")
            self.__ipNet = 10
        
        if("port" in self.__tweaks):
            self.__srvPort = self.__tweaks["port"]
        else:
            self.__logger("MODEL ", "port not in config! Continuing with default value (5000)")
            self.__srvPort = 5000
    
    # Initialize config if it doesn't exist yet
    def __initConfig():
        with open(".weatherdisprc", "w") as conf:
            conf.write("""\
# Weather-Displayer Config File
# This allows you to turn on certain optional functions and change settings to fit your needs. You may ONLY enter
# integers - no strings or booleans. If you want to change it as a boolean, use 0s (false/no) and 1s (true/yes).

# -------- GENERAL CONFIG --------
# This is the main area for configuring the main, integral parts of Weather-Displayer.
#
# web-server:         Turning this on will enable the web-based interface. Weather-Displayer uses Python's Flask library
#                     to run such an interface. You can go to the computer's IP address (displayed on screen) from a browser
#                     to see the interface when enabled, as long as the computer accessing the interface is on the same network
#                     as this computer.
#
# main-display:       Determins whether Weather-Displayer will print out info to the terminal. There will still be text from the
#                     getter and maybe from Flask, but there will be no weather info. If both main-display and web-server are
#                     turned off, only the getter function will be operational.
#
#                     If you are seeing this on a freshly generated config file, main-display is commented out and will not
#                     do anything. I plan on making it functional soon, but right now I'm working on other things.
#
# show-IP:            Determins whether the system's IP Address be displayed. Will be displayed at the top of the terminal
#                     on each update, similar to what happens when web-server is enabled. If both show-IP and web-server are enabled,
#                     web-server's display rules takes precedence.
#
# time:               Determmins if a clock should be displayed. Options include:
#                     0: Don't show clock (default)
#                     1: Show a clock - use 12 hour format
#                     2: Show a clock - use 24 hour format
#
# stop-on-http-error: Determins how to handle fatal HTTP errors. Such errors include 503 and excessive 500 errors. 503 errors
#                     mean that the NWS is working on a solution, thus Weather-Displayer should not continue to request data out
#                     of courtesy to NWS API maintainers. These errors may also last anywhere from an hour or two to days or
#                     weeks. Many 500 errors vanish after waiting a couple seconds, but in other circumstances they may last
#                     longer that this, and should be treated similar to a 503 error. There are 2 ways to handle these:
#                        - Stop Weather-Displayer with a message explaining the situation (default)
#                        - Show backup (but more outdated as time goes on) JSON data. This soulution does not include a message
#                          to the user.
#
# close-timer:       Determins whether the program should wait for user input to close after a crash. Because of important
#                    information to be displayed, the default value is 0. However, especailly in headless environments it
#                    may be desirable for the program to close automatically. In this usecase, the value should be changed
#                    to 1. The program will wait 60 seconds before closing automatically with an exit code of 1.
web-server=0
#main-display=1
show-IP=0
time=0
stop-on-http-error=1
close-timer=0

# -------- WEB INTERFACE CONFIG --------
# This is the area where we will configure the web interface.
#
# ip-network: This setting is directly related to the web-server and does not matter if the web interface is disabled.
#             Weather-Displayer uses ip-network to help calculate which IP address this device is.
#             This should be set to the number in the first octet of your local IP address. For many users, this would be 192,
#             and that is what the default value is. If the script is used on networks that have multiple subnets, such
#             as a workplace or school, it is more likely that this value should be changed to 10. You can use the "ip addr"
#             command on Linux or "ipconfig" command in Windows to find out exactly what you should set it as.
#
# port:       What port should the web-interface run on? By default, it will run on port 80, which is the default in
#             most systems for http traffic. Setting the port to 80, however, will require Weather-Displayer to be run
#             as super user. If you don't want this but still want to use the web interface, change this number to an
#             unused port, such as 5000. Just know that if you do this, you will need to change the url you access
#             the web interface from. For example, with the port being set to 5000 with an IP Address of 192.168.0.50,
#             the url to access the web interface would be http://192.168.0.50:5000
ip-network=192
port=80""")
            conf.close()

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
    def srvPort(self) -> int:
        return self.__srvPort
    
    @property
    def tweaks(self) -> dict:
        return self.__tweaks