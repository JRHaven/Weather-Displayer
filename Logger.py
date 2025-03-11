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

# Make logger an object so that it can be shared

from os import chmod
import time
import os.path

class Logger:
    __logFile = None
    __runningSrv = False
    __logFilePath = ""
    __startTime = None

    def __init__(self, startTime, webInterface: bool=False):
        self.__logFilePath = os.path.join(os.path.dirname(__file__), "log")
        self.__runningSrv = webInterface
        self.__startTime = startTime
    
    def log(self, thread: str, msg: str):
        self.__logFile = open(self.__logFilePath, "a")
        self.__logFile.write(thread + "   [" + str(f"{(time.time() - self.__startTime):f}") + " - " + time.strftime("%m %d %H:%M:%S", time.localtime()) + "]: " + str(msg) + "\n")
        self.__logFile.close()

        # Permissions! If self has a server running on port 80 (may be the case),
        # self will be run as admin and we'll need to change permissions
        if(self.__runningSrv):
            os.chmod(self.__logFilePath, 0o777)
    
    def setRunSrv(self, webInterface: bool):
        self.__runningSrv = webInterface