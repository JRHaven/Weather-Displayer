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

from time import sleep
from Logger import Logger
from states import *
import json, os, math, time, urllib.request

#def getter(logger: Logger):
class Getter():
    __state = None
    __crashOnHTTPError = True
    __logger = None
    __useTimer = 0

    def __init__(self, logger: Logger, crashOnHTTPError: bool, useTimer: int=0):
        self.__logger = logger
        self.__crashOnHTTPError = crashOnHTTPError
        self.__useTimer = useTimer

        # Only set state after every other thing is set
        self.__state = Waiting(self.__stateStack())

    # Return data necessary for state in a tuple
    def __stateStack() -> tuple:
        return tuple(self.__logger, self.__crashOnHTTPError, self.__useTimer)
    
    # Getter for state
    def getState(self):
        return self.__state

    # State resetter - a proper setter isn't necessary
    def resetState(self):
        self.__state = Waiting(__stateStack())

    # Main function
    def run(self):
        # Set this variable for easy identification for logging purposes
        myName = "GETTER"
        # Report to log that script has been started
        logger.log(myName, "JSON Getter Started.")

        # Lets us know if it is our first run
        begin = True

        # We need to load in our NWS info provided by the user in a file. If it doesn't exist, tell the user
        # to get the correct url and provide it in the file
        self.__logger.log(myName, "Locating URL File...")
        if(os.path.exists("url")):
            self.__logger.log(myName, "...Exists! Loading NWS URL")
            with open("url", "r") as destFile:
                dest = destFile.read()
                destFile.close()
        else:
            # The file doesn't exist. Log this occasion and tell main.py to inform and quit
            self.__logger.log(myName, "ERROR: URL File doesn't exist! Informing and Quitting!")
            self.__state = NoURL(self.__stateStack())
            exit(0)

        if(dest[len(dest)-1] == "\n"):
            dest = dest[:-1]

        while(True):
            # Counter for cooldown if need be
            counter = 0
            self.__logger.log(myName, "Attempting to retrieve JSON from NWS API...")

            # Loop to continue trying to download things in case we get a 500 error
            while(True):
                counter += 1
                # If it's been more than 10 tries and we haven't gotten anywhere, we need to give it a break.
                if(counter > 10):
                    criticalHTTPErrorHandler(myName, 500)
                    break
                try:
                    with urllib.request.urlopen(dest) as url:
                        data = json.loads(url.read().decode())
                    if(dest[len(dest)-1] == "/"):
                        with urllib.request.urlopen(dest + "hourly") as url:
                            hourData = json.loads(url.read().decode())
                    else:
                        with urllib.request.urlopen(dest + "/hourly") as url:
                            hourData = json.loads(url.read().decode())
                    
                    self.__logger.log(myName, "JSON Data Successfully Retrieved.")

                    hourGenDate = str(hourData["properties"]["generatedAt"])
                    longGenDate = str(data["properties"]["generatedAt"])
                    today = time.strftime("%Y-%m-%d", time.gmtime())
                    self.__logger.log(myName, "NWS Provided long-term JSON on " + str(data["properties"]["generatedAt"]))
                    self.__logger.log(myName, "NWS Provided hourly JSON on " + str(hourData["properties"]["generatedAt"]))

                    if(today not in longGenDate):
                        self.__logger.log(myName, "ERROR! The NWS provided out of date information for some reason. Waiting some time, then trying again...")
                        # If this is our first time running this script, we should find something to display.
                        # If there is a backup, use that. If not, inform the main script.
                        if((os.path.exists("hourWeatherCache-bk.json") == True) and (os.path.exists("weatherCache-bk.json") == True)):
                            os.rename("hourWeatherCache-bk.json", "hourWeatherCache.json")
                            os.rename("weatherCache-bk.json", "weatherCache.json")
                        else:
                            self.__state = OutDateJSON(self.__stateStack())
                            
                        sleep(300)
                        self.__state = Waiting(self.__stateStack())
                        #continue
                    else:
                        # Use global variable webInterface
                        global webInterface
                        with open("weatherCache.json", "w") as dumpFile:
                            json.dump(data, dumpFile)
                            dumpFile.close()
                        self.__logger.log(myName, "Dumped long-term JSON to file, weatherCache.json")

                        # Permissions! This is probably going to be run as sudo.
                        permGrant(myName, "weatherCache.json", webInterface)
                    
                        with open("hourWeatherCache.json", "w") as hourDumbFile:
                            json.dump(hourData, hourDumbFile)
                            dumpFile.close()
                        self.__logger.log(myName, "Dumped hourly JSON to file, hourWeatherCache.json")

                        # Permissions! This is probably going to be run as sudo.
                        permGrant(myName, "hourWeatherCache.json", webInterface)
                    break
                except urllib.error.HTTPError as e:
                    # We can handle this in different ways depending on the HTTP error given. 500 errors we can handle
                    # by trying again in a couple seconds. 404 errors mean that the url is wrong, report to user.
                    # 503 errors we need to immediately stop everything as to not bog down the NWS's server.
                    if(e.code == 500):
                        self.__logger.log(myName, "HTTP 500 Error. Trying again...")
                        sleep(1)
                        continue
                    elif(e.code == 404):
                        self.__logger.log(myName, "HTTP 404 Error. Notifying main and quitting!")
                        self.__state = WrongURL(self.__stateStack())
                        break
                    elif(e.code == 503):
                        criticalHTTPErrorHandler(myName, 503)
                        break
                # This error occurs if there it cannot resolve the URL, meaning no internet access
                # If there is backup info (which there should be), rename it so that it is avalible
                # to be used
                except urllib.error.URLError as e:
                    # Report to the log
                    self.__logger.log(myName, "URL Error. Could be for a multitude of reasons. The next few lines are error info.")
                    self.__logger.log(myName, str(e))
                    
                    print("Could not connect to the NWS to download new data.")
                    print("Making backups avalible...")
                    if(os.path.exists("weatherCache-bk.json") == True):
                        os.rename("weatherCache-bk.json", "weatherCache.json")
                        self.__logger.log(myName, "Got temporary long-term info from a backup.")
                    else:
                        if(os.path.exists("weatherCache.json") == False):
                            self.__logger.log(myName, "CRITICAL ERROR! No long-term backup info to display! Quitting, there is nothing to do!")
                            self.__state = NoGenJSON(self.__stateStack())
                            break
                        else:
                            self.__logger.log(myName, "Long-Term backups were avalible, using those. Nothing to do now until next cycle.")
                            print("Backups for one weather script is already avalible. There is nothing to do.")
                    
                    if(os.path.exists("hourWeatherCache-bk.json") == True):
                        os.rename("hourWeatherCache-bk.json", "hourWeatherCache.json")
                        self.__logger.log(myName, "Got temporary hourly info from a backup.")
                    else:
                        if(os.path.exists("hourWeatherCache.json") == False):
                            self.__logger.log(myName, "CRITICAL ERROR! No hourly backup info to display! Quitting, there is nothing to do!")
                            self.__state = NoHourJSON(self.__stateStack())
                        else:
                            print("Backups for one weather script is already avalible. There is nothing to do.")
                            self.__logger.log(myName, "Hourly backups were avalible, using those. Nothing to do now until next cycle.")
                    break
                except json.decoder.JSONDecodeError:
                    self.__logger.log(myName, "Encountered JSON decode error. Informing main and quitting...")
                    self.__state = JSONWrongURL(self.__stateStack())
                    break
                begin = False

            # Handle errors, so that we quit this thread if need be
            if(getterCode > 0 and (getterCode < 4 or getterCode > 5)):
                break
            else:
                # Let main know that we have retrieved JSON
                print(getterCode)
                self.__state = NewJSON(self.__stateStack())
                self.__logger.log(myName, "JSON all dealt with here! Getter code set to value of 5...")
                # Tell main that we are now waiting for the next thing, after a second delay
                sleep(1)
                self.__state = Waiting(self.__stateStack())
                self.__logger.log(myName, "Reset Getter code to value of 0: waiting...")
                sleep(900)