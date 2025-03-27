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
from Getter import Getter
from Model import Model
from states.States import *
import json, os, math, time, threading, socket, web

# We're going to need to create a start-time variable to calculate uptime for logging purposes
startTime = time.time()

# Global variables
getterRun = 1

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

def main():
    global crashOnHTTPError, logger
    try:
        # Register logger
        logger = Logger(startTime)

        # Identify ourselves in logging
        myName = "MAIN  "
        logger.log(myName, "Displayer Started.")

        # Initialize model
        model = Model(logger)

        # Register and start getter in a thread
        logger.log(myName, "Starting Getter Thread...")
        getter = Getter(logger, model)
        getterThread = threading.Thread(target=getter.run, daemon=True)
        getterThread.start()

        # Do this with text outputed. We'll do this again without text on the screen later.
        if(os.path.exists("weatherCache.json") == True):
            logger.log(myName, "weatherCache.json still exists. Making it a backup...")
            os.rename("weatherCache.json", "weatherCache-bk.json")
        if(os.path.exists("hourWeatherCache.json") == True):
            logger.log(myName, "hourWeatherCache.json still exists. Making it a backup...")
            os.rename("hourWeatherCache.json", "hourWeatherCache-bk.json")

        # Report to log what tweaks are configured as
        logger.log(myName, "Tweaks Config right before display loop: " + str(model.tweaks))

        print("Waiting for data...")
        while(getter.getState() != NewJSON(model, logger)):
            # Handle any errors that may exist
            error = getter.getState().handleError()
            if(error != None):
                logger.log(myName, "Recieved error from state - quit code " + str(error) + ". Quitting!")
                return error
            
            # wait so we don't overload cpu
            sleep(0.01)
        
        # Data recieved. Let the log know!
        logger.log(myName, "Recieved JSON. Ready to display...")
        
        # Calculate IP if webInterface or show-IP is enabled
        if(model.webInterface or (model.showIP == 1)):
            # Set our IP variable, we'll display this later.
            ip = getIP(model.ipNet)

        # Now that JSON things have been worked out, call for the web interface to start if requested.
        if(model.webInterface):
            webThread = threading.Thread(target=web.main, args=[model, logger], daemon=True)
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
            if(model.useClock != 0):
                # Figure out input string to strftime
                if(model.useClock == 2):
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
            if(model.webInterface):
                # Check if IP is 127.0.0.1. If this IP is given, no IP could be estaablished.
                if(str(ip).strip() == "127.0.0.1"):
                    infoStr += "IP Address could not be calculated."
                else:
                    infoStr += "Web Address: http://" +  str(ip).strip()
            elif(model.showIP == 1):
                # Check if IP is 127.0.0.1. If this IP is given, no IP could be estaablished.
                if(str(ip).strip() == "127.0.0.1"):
                    infoStr += "IP Address could not be calculated."
                else:
                    infoStr += "IP: " +  str(ip).strip()
            
            # Clock. Right now this will be a couple spaces over from rest, but eventually I want it
            # to be justified to the right of the terminal window.
            if(model.useClock != 0):
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
                
                if(getter.getState() == Waiting(model, logger) and i > 1):
                    logger.log(myName, "New JSON recieved. Starting the cycle again.")
                    getter.resetState()

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