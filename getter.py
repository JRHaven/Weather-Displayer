#!/usr/bin/python3

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
import urllib.request, json, os, time

# We're going to need to create a start-time variable to calculate uptime for logging purposes
startTime = time.time()

# Function to write to log file
def log(msg):
    logFile = open("log", "a")
    logFile.write("GETTER.PY [" + str(f"{(time.time() - startTime):f}") + " - " + time.strftime("%m %d %H:%M:%S", time.localtime()) + "]: " + str(msg) + "\n")
    logFile.close()
def wrtComm(msg):
    comm = open("passthru", "w")
    comm.write(msg)
    comm.close()
def rdComm():
    comm = open("passthru", "r")
    msg = comm.read()
    comm.close()
    return msg
def chkTerminate():
    comms = rdComm()
    if("don" in comms):
        log("Quit message revieved, quitting")
        return True
    else:
        return False

# Main Function
def main():
    # Report to log that script has been started
    log("JSON Getter Started.")

    # Lets us know if it is our first run
    begin = True

    # We need to load in our NWS info provided by the user in a file. If it doesn't exist, tell the user
    # to get the correct url and provide it in the file
    log("Locating URL File...")
    if(os.path.exists("url")):
        log("...Exists! Loading NWS URL")
        with open("url", "r") as destFile:
            dest = destFile.read()
    else:
        # The file doesn't exist. Log this occasion and tell main.py to inform and quit
        log("ERROR: URL File doesn't exist! Informing and Quitting!")
        with open("passthru", "w") as comms:
            comms.write("nourl")
            sleep(1)
            comms.write("")
        return 1

    while(True):
        # Use this variable to find out if we failed to download data or not
        fail = False

        log("Attempting to retrieve JSON from NWS API...")

        # Loop to continue trying to download things in case we get a 500 error
        while(True):
            try:
                with urllib.request.urlopen(dest) as url:
                    data = json.loads(url.read().decode())
                if(dest[len(dest)-1] == "/"):
                    with urllib.request.urlopen(dest + "hourly") as url:
                        hourData = json.loads(url.read().decode())
                else:
                    with urllib.request.urlopen(dest + "/hourly") as url:
                        hourData = json.loads(url.read().decode())
                
                log("JSON Data Successfully Retrieved.")
                hourGenDate = str(hourData["properties"]["generatedAt"])
                longGenDate = str(data["properties"]["generatedAt"])
                today = time.strftime("%Y-%m-%d", time.gmtime())
                log("NWS Provided long-term JSON on " + str(data["properties"]["generatedAt"]))
                log("NWS Provided hourly JSON on " + str(hourData["properties"]["generatedAt"]))

                if(today not in longGenDate):
                    fail = True
                    log("ERROR! The NWS provided out of date information for some reason. Waiting some time, then trying again...")
                    # If this is our first time running this script, we should find something to display.
                    # If there is a backup, use that. If not, inform the main script.
                    if((os.path.exists("hourWeatherCache-bk.json") == True) and (os.path.exists("weatherCache-bk.json") == True)):
                        os.rename("hourWeatherCache-bk.json", "hourWeatherCache.json")
                        os.rename("weatherCache-bk.json", "weatherCache.json")
                    else:
                        wrtComm("OUTDATE")
                        sleep(5)
                        wrtComm("")
                        
                    for i in range(1,3000):
                        comms = rdComm()
                        if("don" in comms):
                            log("Quit message revieved, quitting")
                            return 0
                        else:
                            sleep(0.1)
                    continue
                else:
                    fail = False
                
                if(fail == False):
                    with open("weatherCache.json", "w") as dumpFile:
                        json.dump(data, dumpFile)
                        dumpFile.close()
                        log("Dumping long-term JSON to file, weatherCache.json")
                
                    with open("hourWeatherCache.json", "w") as hourDumbFile:
                        json.dump(hourData, hourDumbFile)
                        dumpFile.close()
                        log("Dumping hourly JSON to file, hourWeatherCache.json")
                break
                # If there was an error while doing this, void it.
                #if(os.path.exists("late-error") == True):
                #    os.remove("late-error")
            except urllib.error.HTTPError as e:
                # We've gotten a 500 error. This goes away after a second or so, so let's try again
                print("[ GETTER ERROR ] Could not get weather data! Trying Again...")
                # Report to log
                log("HTML Error, probably a 500 error. Trying again. The next few lines is the error info.")
                log(str(e))

                # Check for termination signal
                if(chkTerminate()):
                    return 0
                sleep(1)
            # This error occurs if there it cannot resolve the URL, meaning no internet access
            # If there is backup info (which there should be), rename it so that it is avalible
            # to be used
            except urllib.error.URLError as e:
                # Report to the log
                log("URL Error. Could be for a multitude of reasons. The next few lines are error info.")
                log(str(e))
                fail = True
                print("Could not connect to the NWS to download new data.")
                print("Making backups avalible...")
                if(os.path.exists("weatherCache-bk.json") == True):
                    os.rename("weatherCache-bk.json", "weatherCache.json")
                    log("Got temporary long-term info from a backup.")
                else:
                    if(os.path.exists("weatherCache.json") == False):
                        print("Oops! There's no data to use! Quit this program, check the \
internet connection, and try again! Exiting...")
                        log("CRITICAL ERROR! No long-term backup info to display! Quitting, there is nothing to do!")
                        return 1
                    else:
                        log("Long-Term backups were avalible, using those. Nothing to do now until next cycle.")
                        print("Backups for one weather script is already avalible. There is nothing to do.")
                
                if(os.path.exists("hourWeatherCache-bk.json") == True):
                    os.rename("hourWeatherCache-bk.json", "hourWeatherCache.json")
                    log("Got temporary hourly info from a backup.")
                else:
                    if(os.path.exists("hourWeatherCache.json") == False):
                        print("Oops! There's no data to use! Quit this program, check the \
internet connection, and try again! Exiting...")
                        log("CRITICAL ERROR! No hourly backup info to display! Quitting, there is nothing to do!")
                        return 1
                    else:
                        print("Backups for one weather script is already avalible. There is nothing to do.")
                        log("Hourly backups were avalible, using those. Nothing to do now until next cycle.")
                break
            begin = False

        for i in range(1,9000):
            comms = rdComm()
            if(chkTerminate()):
                return 0
            else:
                sleep(0.1)

# Execution
if(__name__ == "__main__"):
    exit(main())
