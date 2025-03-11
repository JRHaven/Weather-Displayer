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
from Logger import Logger
import json, os, math, time, threading, urllib.request, socket, web

# We're going to need to create a start-time variable to calculate uptime for logging purposes
startTime = time.time()

# Create a seperate return code variable for getter
"""

  Codes and Meanings
 -=-=-=-=-=-=-=-=-=-=

0: Waiting
1: No URL File, this will quit the getter
2: Cannot retrieve general weather JSON data, this will quit the getter
3: Cannot retrieve hourly weather JSON data, this will quit the getter
4: The date on the JSON timestamp does not match today's date. This is not a critical error; will not quit the getter.
5: New JSON!
6: 404 error encountered. This would mean the provided url is incorrect, this will quit the getter.
7: 503 error encountered. If crashOnHTTPError is set to True, this will quit the getter. If not, it will be handled by main().
8: Needed backups don't exist, this will quit the getter
9: Excessive 500 errors, this will quit the getter if configured to do so.
10: Encountered json.decoder.JSONDecodeError. This almost certainly means the user provided the wrong url, this will quit the getter

"""

# Global variables that should be accessible to both threads
getterCode = 0
getterRun = 1
crashOnHTTPError = True
webInterface = False
logger = None

# Deal with permissions only if web-server is enabled. If it is disabled, the program is probably not being run
# as sudo and thus doesn't require changing file permissions.
def permGrant(myName, file, serverEnabled=False):
    if(serverEnabled):
        log(myName, "Web Interface enabled. Granting full permission to " + file + "...")
        # Use try to ignore if file not exists error
        try:
            os.chmod(file, 0o777)
        except FileNotFoundError:
            log(myName, file + " vanished! Permissions could not be granted. Moving on!")

# I need to refactor my code lol
def criticalHTTPErrorHandler(myName: str, errorCode: int):
    global crashOnHTTPError, getterCode
    if(crashOnHTTPError):
        if(errorCode == 500):
            log(myName, "Too many 500 errors! There\'s something deeper going on. Configured to crash. Notifying main and quitting!")
            getterCode = 9
        else:
            log(myName, "HTTP " + str(errorCode) + " Error. Configured to crash. Notifying main and quitting!")
            getterCode = 7

    else:
        if(errorCode == 500):
            log(myName, "Too many 500 errors! There\'s something deeper going on. Configured to continue. Implementing backups if they exist...")
            getterCode = 9
        else:
            log(myName, "HTTP " + str(errorCode) + " Error. Configured to continue. Implementing backups if they exist...")

        if(os.path.exists("weatherCache-bk.json") and os.path.exists("hourWeatherCache-bk.json")):
            os.rename("weatherCache-bk.json", "weatherCache.json")
            os.rename("hourWeatherCache-bk.json", "hourWeatherCache.json")
        else:
            log(myName, "CRITICAL ERROR! No or incomplete weather backups to display! Quitting, there is nothing to do!")
            getterCode = 8

def getter(logger: Logger):
    global getterCode, crashOnHTTPError

    # Set this variable for easy identification for logging purposes
    myName = "GETTER"
    # Report to log that script has been started
    logger.log(myName, "JSON Getter Started.")

    # Lets us know if it is our first run
    begin = True

    # We need to load in our NWS info provided by the user in a file. If it doesn't exist, tell the user
    # to get the correct url and provide it in the file
    logger.log(myName, "Locating URL File...")
    if(os.path.exists("url")):
        logger.log(myName, "...Exists! Loading NWS URL")
        with open("url", "r") as destFile:
            dest = destFile.read()
            destFile.close()
    else:
        # The file doesn't exist. Log this occasion and tell main.py to inform and quit
        logger.log(myName, "ERROR: URL File doesn't exist! Informing and Quitting!")
        getterCode = 1
        exit(0)

    if(dest[len(dest)-1] == "\n"):
        dest = dest[:-1]

    while(True):
        # Counter for cooldown if need be
        counter = 0
        logger.log(myName, "Attempting to retrieve JSON from NWS API...")

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
                
                logger.log(myName, "JSON Data Successfully Retrieved.")

                hourGenDate = str(hourData["properties"]["generatedAt"])
                longGenDate = str(data["properties"]["generatedAt"])
                today = time.strftime("%Y-%m-%d", time.gmtime())
                logger.log(myName, "NWS Provided long-term JSON on " + str(data["properties"]["generatedAt"]))
                logger.log(myName, "NWS Provided hourly JSON on " + str(hourData["properties"]["generatedAt"]))

                if(today not in longGenDate):
                    logger.log(myName, "ERROR! The NWS provided out of date information for some reason. Waiting some time, then trying again...")
                    # If this is our first time running this script, we should find something to display.
                    # If there is a backup, use that. If not, inform the main script.
                    if((os.path.exists("hourWeatherCache-bk.json") == True) and (os.path.exists("weatherCache-bk.json") == True)):
                        os.rename("hourWeatherCache-bk.json", "hourWeatherCache.json")
                        os.rename("weatherCache-bk.json", "weatherCache.json")
                    else:
                        getterCode = 4
                        
                    sleep(300)
                    getterCode = 0
                    #continue
                else:
                    # Use global variable webInterface
                    global webInterface
                    with open("weatherCache.json", "w") as dumpFile:
                        json.dump(data, dumpFile)
                        dumpFile.close()
                    logger.log(myName, "Dumped long-term JSON to file, weatherCache.json")

                    # Permissions! This is probably going to be run as sudo.
                    permGrant(myName, "weatherCache.json", webInterface)
                
                    with open("hourWeatherCache.json", "w") as hourDumbFile:
                        json.dump(hourData, hourDumbFile)
                        dumpFile.close()
                    logger.log(myName, "Dumped hourly JSON to file, hourWeatherCache.json")

                    # Permissions! This is probably going to be run as sudo.
                    permGrant(myName, "hourWeatherCache.json", webInterface)
                break
            except urllib.error.HTTPError as e:
                # We can handle this in different ways depending on the HTTP error given. 500 errors we can handle
                # by trying again in a couple seconds. 404 errors mean that the url is wrong, report to user.
                # 503 errors we need to immediately stop everything as to not bog down the NWS's server.
                if(e.code == 500):
                    logger.log(myName, "HTTP 500 Error. Trying again...")
                    sleep(1)
                    continue
                elif(e.code == 404):
                    logger.log(myName, "HTTP 404 Error. Notifying main and quitting!")
                    getterCode = 6
                    break
                elif(e.code == 503):
                    criticalHTTPErrorHandler(myName, 503)
                    break
            # This error occurs if there it cannot resolve the URL, meaning no internet access
            # If there is backup info (which there should be), rename it so that it is avalible
            # to be used
            except urllib.error.URLError as e:
                # Report to the log
                logger.log(myName, "URL Error. Could be for a multitude of reasons. The next few lines are error info.")
                logger.log(myName, str(e))
                
                print("Could not connect to the NWS to download new data.")
                print("Making backups avalible...")
                if(os.path.exists("weatherCache-bk.json") == True):
                    os.rename("weatherCache-bk.json", "weatherCache.json")
                    logger.log(myName, "Got temporary long-term info from a backup.")
                else:
                    if(os.path.exists("weatherCache.json") == False):
                        logger.log(myName, "CRITICAL ERROR! No long-term backup info to display! Quitting, there is nothing to do!")
                        getterCode = 2
                        break
                    else:
                        logger.log(myName, "Long-Term backups were avalible, using those. Nothing to do now until next cycle.")
                        print("Backups for one weather script is already avalible. There is nothing to do.")
                
                if(os.path.exists("hourWeatherCache-bk.json") == True):
                    os.rename("hourWeatherCache-bk.json", "hourWeatherCache.json")
                    logger.log(myName, "Got temporary hourly info from a backup.")
                else:
                    if(os.path.exists("hourWeatherCache.json") == False):
                        logger.log(myName, "CRITICAL ERROR! No hourly backup info to display! Quitting, there is nothing to do!")
                        getterCode = 3
                    else:
                        print("Backups for one weather script is already avalible. There is nothing to do.")
                        logger.log(myName, "Hourly backups were avalible, using those. Nothing to do now until next cycle.")
                break
            except json.decoder.JSONDecodeError:
                logger.log(myName, "Encountered JSON decode error. Informing main and quitting...")
                getterCode = 10
                break
            begin = False

        # Handle errors, so that we quit this thread if need be
        if(getterCode > 0 and (getterCode < 4 or getterCode > 5)):
            break
        else:
            # Let main know that we have retrieved JSON
            print(getterCode)
            getterCode = 5
            logger.log(myName, "JSON all dealt with here! Getter code set to value of 5...")
            # Tell main that we are now waiting for the next thing, after a second delay
            sleep(1)
            getterCode = 0
            logger.log(myName, "Reset Getter code to value of 0: waiting...")
            sleep(900)
        

def initConfig():
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

def decodeTemps(data):
    temps = []
    periods = data["properties"]["periods"]
    for i in periods:
        temps.append(i["temperature"])
    return temps

def decodeTempUnit(data):
    temps = []
    periods = data["properties"]["periods"]
    for i in periods:
        temps.append(i["temperatureUnit"])
    return temps

def decodeTitles(data):
    titles = []
    periods = data["properties"]["periods"]
    for i in periods:
        titles.append(i["name"])
    return titles

def decodeForecasts(data):
    forecast = []
    periods = data["properties"]["periods"]
    for i in periods:
        forecast.append(i["shortForecast"])
    return forecast

def decodeWindSpeed(data):
    forecast = []
    periods = data["properties"]["periods"]
    for i in periods:
        forecast.append(i["windSpeed"])
    return forecast

def decodeWindDir(data):
    forecast = []
    periods = data["properties"]["periods"]
    for i in periods:
        forecast.append(i["windDirection"])
    return forecast

def artDisplay(forecast):
    if(("Partly Sunny" in forecast) or ("Partly Cloudy" in forecast)):
        return '''             \\      |    /
              \\  ,g88R_ /  
                  d888(`  ).
         -  --==  888(     ).=--
        )         Y8P(       '`.
                .+(`(      .   ) .--
               ((    (..__.:'-.=(   )
         )      ` __.:'   ) (   (   ))''' # Credit to https://ascii.co.uk/art/clouds
    elif("Mostly Sunny" in forecast):
        return '''    ,--.:::::::::::::::::::::::::::::....:::::::
        ):::::::::::::::::::::::::..      ..::::
      _'-. _::::::::::::::::::::..   ,--.   ..::
     (    ) ),--.:::::::::::::::.   (    )   .::
                 )-._:::::::::::..   `--'   ..::
    _________________)::::::::::::..      ..::::''' # Credit: https://ascii.co.uk/art/clouds
    elif((forecast == "Cloudy") or (forecast == "Mostly Cloudy")):
        return '''                    ███████████            
                  ██          ████          
                ██              ▒▒██        
            ████▒▒                ██        
      ██████      ▒▒            ▒▒▒▒████    
    ██▒▒            ▒▒        ▒▒      ▒▒██  
    ██▒▒▒▒           ▒▒▒▒▒▒▒▒▒          ▒▒██
      ████████████████████████████████████  ''' # Credit: https://textart.sh/topic/cloud
    elif(forecast == "Sunny"):
        return '''                      ,
                      :
         '.        _______       .'
           '  _.-"`       `"-._ '
            .'                 '.
     `'--. /                     \\ .--'`
          /                       \\
      '   |                       |  '-.'''
    elif("clear" in forecast.lower()):
        return '''    --------------------------------
    --------------------------------
    -------------------- ________ --
    --------------- ____/ +      \\__
    -------------- (       -
    ---- _________/    *      =
    ____/    `     @             :'''
    elif(("rain/snow" in forecast.lower()) or ("sleet" in forecast.lower())):
        return '''                      ██████            
                    ██      ████      
              ████▒▒           ███   
           ██▒▒    ▒▒        ▒▒   ▒▒██
         ██         ▒▒▒▒▒▒▒▒▒▒      ▒▒██
        █████████████████████████████████
           i  * i  * i  * i    i*   *
         *   i  * i  * i  *  i *   i  *   '''
    elif((("showers" in forecast.lower()) or ("shower" in forecast.lower()) or ("drizzle" in forecast.lower())) and ("slight" not in forecast.lower()) and ("snow" not in forecast.lower())):
        return '''                      ██████            
                    ██      ████      
              ████▒▒           ███   
           ██▒▒    ▒▒        ▒▒   ▒▒██
         ██         ▒▒▒▒▒▒▒▒▒▒      ▒▒██
        █████████████████████████████████ 
           i    i    i     i      i 
             i    i   i   i     i   '''
    elif(("snow" in forecast.lower()) or ("snow shower" in forecast.lower())):
        return '''                      ██████            
                    ██      ████      
              ████▒▒           ███   
           ██▒▒    ▒▒        ▒▒   ▒▒██
         ██         ▒▒▒▒▒▒▒▒▒▒      ▒▒██
        █████████████████████████████████ 
           *    *    *     *      * 
         *    *    *    *      *    *    '''
    elif(("rain" in forecast.lower()) and not ("slight" in forecast.lower()) and not ("shower" in forecast.lower())):
        return '''              0      00  000000000000
             0000 0  0000000000000000000
      000000000000000000000000000000000000
   000000000000000000000000000000000000000000
       0000000000000000000000000000000
          / / / / / / / / / / / / /
        / / / / / / / / / / / /
        / / / / / / / / / /''' # Credit: https://www.asciiart.eu/nature/rains
    elif((forecast == "Slight Chance Rain Showers") or (forecast == "Slight Chance Showers And Thunderstorms")):
        return '''                    ███████████            
                  ██          ████          
                ██              ▒▒██        
            ████▒▒                ██        
      ██████      ▒▒            ▒▒▒▒████    
    ██▒▒            ▒▒        ▒▒      ▒▒██  
    ██▒▒▒▒           ▒▒▒▒▒▒▒▒▒          ▒▒██
      ████████████████████████████████████  ''' # Credit: https://textart.sh/topic/cloud
    elif("fog" in forecast.lower()):
        return '''    ---///---///---///---///---///---///
    ///-ffffff//-ooooooo/--gggggg-///---
    ---/fff--///-o-///-o-//g---/g/---///
    ///-ffffff--/o/-o-/o/--gggggg-///---
    ---/fff--///-o-///-o-///---/g/---///
    ///-fff//---/ooooooo/--gggggg-///---
    ---///---///---///---///---///---///'''
    elif("haze" in forecast.lower()):
        return '''    \\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/
    /\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\
    \\/\\/\\/\\/\\/\\/\\/\\/\\/\\/ ________ \\/
    /\\/\\/\\/\\/\\/\\/\\/ ____/ +      \\__
    \\/\\/\\/\\/\\/\\/\\/ (       -
    /\\/\\ _________/    *      =
    ____/    `     @             :'''
    else:
        # First we have to find the characters in the longest word, then center it approprietally.
        # This is what i'm planning (this is a placeholder if the forecast isn't recognized):
        '''
            +-------------+
            | M o s t l y |
            |  S u n n y  |
            +-------------+
        '''

        # End string to return
        endStr = ""

        # First! Calculate the amount of letters in the longest word. This will be needed
        # to center the text.
        words = forecast.split(" ")
        letters = 0
        for i in words:
            if(len(i) > letters):
                letters = len(i)

        # Now we need to compute exactly how many dashes we will need on the top row.
        # That is, the letters multiplied by two and then add two for padding.
        dashCount = letters * 2 + 2

        # Now let's draw the top line.
        endStr += "        +"
        for i in range(1, dashCount):
            endStr += "-"
        endStr += "+\n"

        # Cool! Now let's get into the meat and potatoes of this. Repeat this next thing for every word.
        for i in words:
            # Starting stuffs
            endStr += "        | "

            # We need to find out how many spaces to put in front to space things out. We
            # can do this by making use of our old letters variable.
            spaces = letters - len(i)
            for j in range(0, spaces):
                endStr += " "
            
            # Finally start printing out letters and spaces
            inc = 0
            for j in i:
                if(inc == letters):
                    endStr += j
                else:
                    endStr += j + " "
                inc += 1
            
            # Now we need to add spaces again.
            for j in range(0, spaces):
                endStr += " "
            
            # Finish up
            endStr += "|\n"
        
        # Do the last line of dashes
        endStr += "        +"
        for i in range(1, dashCount):
            endStr += "-"
        endStr += "+"

        # Return
        return endStr

def getIP(network):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Connect the socket to a dummy IP address on the LAN (255.255.255.255), and any unused port
        # This step is necessary to obtain the local IP address of the socket.
        fetIP = str(network) + ".255.255.255"
        s.connect((fetIP, 1))
        
        # Get the local IP address of the socket
        ip = s.getsockname()[0]
    except:
        # If there is an error, return the loopback address (127.0.0.1)
        ip = '127.0.0.1'
    finally:
        # Close the socket
        s.close()
    
    # Return the local IP address as a string
    return ip

def errorMsg(logMsg: str, msg: str, useTimer=0):
    global logger
    myName = "MAIN  "
    logger.log(myName, logMsg)
    os.system("clear")
    print(msg)
    
    if(useTimer == 1):
        logger.log(myName, "Configured to quit automatically. Will close in 60 seconds.")
        sleep(60)
    else:
        input("Press enter to exit...")
    
    logger.log(myName, "Quitting with exit value of 1!")
    return 1


# Check for problematic getter codes function. For use in main() only
def checkForIssues(useTimer=0):
    # Checking the global getterCode variable will be necessary.
    global getterCode, logger
    if(getterCode == 4):
        # We've found out that the data we got is out of data, and we have no backups!
        # Display something!
        logger.log(myName, "Recieved Out of Date Message")
        os.system("cowsay -d \"Inaccurate Data\"")
        sleep(300)
    elif(getterCode == 2):
        # Critical error, couldn't retrieve general weather data.
        return errorMsg("Recieved getterCode 2. Prompting user to quit...", \
            "Could not retrieve general weather data.\nWeather-Displayer cannot continue.", useTimer)
    elif(getterCode == 3):
        # Similar error, handled in the exact same way
        return errorMsg("Recieved getterCode 3. Prompting user to quit...", \
            "Could not retrieve hourly weather data.\nWeather-Displayer cannot continue.", useTimer)
    elif(getterCode == 6):
        # Encountered 404 error
        return errorMsg("Recieved message of 404 error. Telling user and quitting...",\
            "Recieved a 404 error. This likely means the url given \
in the url file is incorrect.\nRetry the process of finding the API URL and try again.", useTimer)
    elif(getterCode == 7):
        # Encountered 503 error
        return errorMsg("Recieved message of 503 error. Telling the user and quitting...", \
            "Recieved a 503 error. This is an error on the NWS end, usually\n\
meaning the server down, possibly under maintenance.\n\
Weather-Displayer cannot continue. Try again in a few hours.", useTimer)
    elif(getterCode == 8):
        return errorMsg("Recieved message on lack of backups. Telling the user and quitting...", \
            "Was unable to acquire needed backups to sort out an error.\nWeather-Displayer cannot continue.", useTimer)
    elif(getterCode == 9):
        return errorMsg("Recieved message of excessive 500 errors. Telling the user and quitting...", \
            "Recieved too many 500 errors. Usually these clear after a couple seconds,\n\
but not now. This is a NWS issue. Weather-Displayer cannot continue.\n\
Try again in a couple hours.", useTimer)
    elif(getterCode == 10):
        return errorMsg("Recieved message of decode error. Telling user and quitting...", \
            "Encountered JSON decode error. This is likely the\nresult of an incorrect url.\n\
Retry the process of finding the API URL and try again.", useTimer)

def main():
    global getterCode, crashOnHTTPError, logger
    try:
        # Register logger
        logger = Logger(startTime)

        # Identify ourselves in logging
        myName = "MAIN  "
        logger.log(myName, "Displayer Started.")

        # If the config file doesn't exist, initialize!
        logger.log(myName, "Loading configurations...")
        if(not os.path.exists(".weatherdisprc")):
            logger.log(myName, ".weatherdisprc doesn't exist! Initializing...")
            initConfig()

        # We are going to store our configs in a dictionary
        tweaks = {}
        with open(".weatherdisprc", "r") as config:
            # Take out trailing whitespace, and then loop
            for i in config.read().strip().split("\n"):
                if(i == ""):
                    continue
                if(i[0] == "#"):
                    continue

                element = i.split("=")
                try:
                    tweaks[element[0]] = int(element[1])
                except ValueError:
                    logger.log(myName, "ERROR: Cannot convert to int! Skipping, with dummy value of 0.")
                    tweaks[element[0]] = 0
            config.close()
        
        # Identify global variable webInterface so that getter will know whether to change file permissions, and for
        # a more reliable way of checking if the web interface is enabled
        global webInterface

        # Use try statement to detect a KeyError
        try:
            if(tweaks["web-server"] == 1):
                webInterface = True

                # The port variable is essential in this case.
                if("port" not in tweaks):
                    tweaks["port"] = 80
        except KeyError:
            logger.log(myName, "web-server variable not found in config file! Keeping webInterface set to false.")
        
        # Tell the logger what the status of webInterface is
        logger.setRunSrv(webInterface)

        if("stop-on-http-error" in tweaks):
            if(tweaks["stop-on-http-error"] == 0):
                crashOnHTTPError = False
        else:
            logger.log(myName, "stop-on-http-error variable not found in config file! Keeping crashOnHTTPError set to true.")

        # Ensure time variable is initialized
        if("time" not in tweaks):
            tweaks["time"] = 0
        
        # Check if we need to show IP - we'll need this later.
        if("show-IP" in tweaks):
            showIP = tweaks["show-IP"]
        else:
            showIP = 0
            logger.log(myName, "Showing IP config isn't configured! Using default value of false.")

        # Threading Things. Start with getter for now, we'll do the server if it is needed after we get data.
        logger.log(myName, "Starting Getter Thread...")
        getterThread = threading.Thread(target=getter, daemon=True, args=[logger])
        getterThread.start()

        # Do this with text outputed. We'll do this again without text on the screen later.
        if(os.path.exists("weatherCache.json") == True):
            logger.log(myName, "weatherCache.json still exists. Making it a backup...")
            os.rename("weatherCache.json", "weatherCache-bk.json")
        if(os.path.exists("hourWeatherCache.json") == True):
            logger.log(myName, "hourWeatherCache.json still exists. Making it a backup...")
            os.rename("hourWeatherCache.json", "hourWeatherCache-bk.json")

        # Report to log what tweaks are configured as
        logger.log(myName, "Tweaks Config right before display loop: " + str(tweaks))

        print("Waiting for data...")
        while(getterCode != 5):
            # Check for various getter messages
            if(getterCode == 1):
                # There is no URL File
                if("close-timer" in tweaks):
                    return errorMsg("Recieved No URL Message...", \
                        "\nERROR: Could not find the NWS Destination URL!\n\
If this is your first time running the script, you may have not\nput in the \
destination URL. If you don't know how to do this,\ngo to https://github.com/JR-Tech-and-Software/Weather-Displayer\n\
and read the README.md file to explain the steps to do this.", tweaks["close-timer"])
                else:
                    return errorMsg("Recieved No URL Message...", \
                        "\nERROR: Could not find the NWS Destination URL!\n\
If this is your first time running the script, you may have not\nput in the \
destination URL. If you don't know how to do this,\ngo to https://github.com/JR-Tech-and-Software/Weather-Displayer\n\
and read the README.md file to explain the steps to do this.")

            # Check for getter errors, return the value if there is a value to return
            if("close-timer" in tweaks):
                issuesCode = checkForIssues(tweaks["close-timer"])
            else:
                issuesCode = checkForIssues()
            
            if(issuesCode != None):
                return issuesCode

            # wait so we don't destroy cpu fan lol
            sleep(0.01)
        
        # Data recieved. Let the log know!
        logger.log(myName, "Recieved JSON. Ready to display...")
        
        # Calculate IP if webInterface or show-IP is enabled
        if(webInterface or (showIP == 1)):
            # Set our IP variable, we'll display this later.
            ip = getIP(tweaks["ip-network"])

        # Now that JSON things have been worked out, call for the web interface to start if requested.
        if(webInterface):
            webThread = threading.Thread(target=web.main, args=[tweaks["port"], logger], daemon=True)
            webThread.start()

            # Wait for Flask to get running before continuing
            sleep(10)

        # Get our json data from files
        while(True):
            try:
                with open("weatherCache.json", "r") as theData:
                    data = json.load(theData)
                    theData.close()
                with open("hourWeatherCache.json", "r") as theData:
                    hourData = json.load(theData)
                    theData.close()
                break
            except json.decoder.JSONDecodeError as e:
                logger.log(myName, "Couldn't decode the JSON. Trying again. Next few lines contain error information.")
                logger.log(myName, str(e))
                sleep(1)
            except FileNotFoundError:
                logger.log(myName, "Could not find JSON. Trying again in 2 secs...")
                sleep(2)
        
        # Get decoded data in arrays using functions above
        logger.log(myName, "Decoding JSON Data...")
        currentTemps = decodeTemps(data)
        tempUnits = decodeTempUnit(data)
        titles = decodeTitles(data)
        forecasts = decodeForecasts(data)
        windSpeed = decodeWindSpeed(hourData)
        windDir = decodeWindDir(hourData)
        hourForecast = decodeForecasts(hourData)
        nowTemp = decodeTemps(hourData)

        # Counter we will need later
        i = 0

        # This ENTIRE thing should be repeated
        while(True):
            # Get current time (if enabled)
            if(tweaks["time"] != 0):
                # Figure out input string to strftime
                if(tweaks["time"] == 2):
                    timeMakStr = "%H:%M"
                else:
                    timeMakStr = "%I:%M %p"
                timeStr = time.strftime(timeMakStr, time.localtime())

            # Now time for the meat and potatoes of this script: Displaying weather data
            os.system("clear")

            #for i in range(0,4):
            #    print(titles[i] + ": " + forecasts[i] + ". Temp: " + str(currentTemps[i]) + "°" + tempUnits[i])
            
            # Print out display
            logger.log(myName, "Printing out display...")

            # Heading Info Line. Depending on what options are enabled, it could consist of nothing, an IP Address,
            # a web server URL, and/or a clock. Thus, use a variable to help us out.
            infoStr = ""
            # If web server was requested, print out IP Address
            if(webInterface):
                # Check if IP is 127.0.0.1. If this IP is given, no IP could be estaablished.
                if(str(ip).strip() == "127.0.0.1"):
                    infoStr += "IP Address could not be calculated."
                else:
                    infoStr += "Web Address: http://" +  str(ip).strip()
            elif(showIP == 1):
                # Check if IP is 127.0.0.1. If this IP is given, no IP could be estaablished.
                if(str(ip).strip() == "127.0.0.1"):
                    infoStr += "IP Address could not be calculated."
                else:
                    infoStr += "IP: " +  str(ip).strip()
            
            # Clock. Right now this will be a couple spaces over from rest, but eventually I want it
            # to be justified to the right of the terminal window.
            if(tweaks["time"] != 0):
                if(infoStr != ""):
                    infoStr += "   " + timeStr
                else:
                    infoStr = timeStr
            
            # Print the info string
            print(infoStr)


            print(artDisplay(hourForecast[0]))
            print("        ", hourForecast[0])
            print("Current Temperature:", str(nowTemp[0]) + ",",
                    titles[1] + "'s Temperature:\n" + str(currentTemps[1]) + ",",
                    titles[2] + "'s Temperature:", str(currentTemps[2]))
            print("The wind:", windDir[0], "at", windSpeed[0] + ".")

            while(True):
                sleep(0.5)
                if(((i % 120) == 0) and (i > 1)):
                    i += 1
                    break
                elif(i == 0):
                    # All the things we need to do to wrap up displaying
                    logger.log(myName, "Display has completed. Time to manage JSON files then wait.")

                    """ We now need to clear all cached files so that we can update it again.
                        To do this, we'll simply make backup files (so that in the case there)
                        is no internet to download, we can simply use those. """

                    if(os.path.exists("weatherCache.json") == True):
                        if(os.path.exists("weatherCache-bk.json") == True):
                            logger.log(myName, "Previous long-term backups exist! Deleting them to ensure no confusion")
                            os.remove("weatherCache-bk.json")
                        os.rename("weatherCache.json", "weatherCache-bk.json")
                        logger.log(myName, "Transfering JSON files to backup...")
                    if(os.path.exists("hourWeatherCache.json") == True):
                        if(os.path.exists("hourWeatherCache-bk.json") == True):
                            logger.log(myName, "Previous hourly backups exist! Deleting them to ensure no confusion")
                            os.remove("hourWeatherCache-bk.json")
                        os.rename("hourWeatherCache.json", "hourWeatherCache-bk.json")
                        logger.log(myName, "Transfering Hourly JSON files to backup...")
                
                if(getterCode == 5 and i > 1):
                    logger.log(myName, "New JSON recieved. Starting the cycle again.")
                    getterCode = 0

                    # Reset Counter
                    i = 0

                    # Get our json data from files
                    while(True):
                        try:
                            with open("weatherCache.json", "r") as theData:
                                data = json.load(theData)
                                theData.close()
                            with open("hourWeatherCache.json", "r") as theData:
                                hourData = json.load(theData)
                                theData.close()
                            break
                        except json.decoder.JSONDecodeError as e:
                            logger.log(myName, "Couldn't decode the JSON. Trying again. Next few lines contain error information.")
                            sleep(1)
                        except FileNotFoundError:
                            logger.log(myName, "Could not find JSON. Trying again in 2 secs...")
                            sleep(2)
                        
                    # Get decoded data in arrays using functions above
                    logger.log(myName, "Decoding JSON Data...")
                    currentTemps = decodeTemps(data)
                    tempUnits = decodeTempUnit(data)
                    titles = decodeTitles(data)
                    forecasts = decodeForecasts(data)
                    windSpeed = decodeWindSpeed(hourData)
                    windDir = decodeWindDir(hourData)
                    hourForecast = decodeForecasts(hourData)
                    nowTemp = decodeTemps(hourData)

                    break
                else:
                    if(i == 7200):
                        logger.log(myName, "Still waiting for JSON Data. Hasn't been recieved in a long time.")
                        print("Weather info hasn't updated in a while. Try restarting the system.\nIf problems presist, check the log.")
                
                if(i < 7202):
                    i += 1
    except KeyboardInterrupt:
        # Final things to be done
        logger.log(myName, "Keyboard Interrupt - Quitting!")
        return 0

if(__name__ == "__main__"):
    exit(main())