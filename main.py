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
import json, os, sys, math, time

# We're going to need to create a start-time variable to calculate uptime for logging purposes
startTime = time.time()

# Function to write to log file
def log(msg):
    logFile = open("log", "a")
    logFile.write("MAIN.PY   [" + str(f"{(time.time() - startTime):f}") + " - " + time.strftime("%m %d %H:%M:%S", time.localtime()) + "]: " + str(msg) + "\n")
    logFile.close()
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
        print('''
             \\      |    /
              \\  ,g88R_ /  
                  d888(`  ).
         -  --==  888(     ).=--
        )         Y8P(       '`.
                .+(`(      .   ) .--
               ((    (..__.:'-.=(   )
         )      ` __.:'   ) (   (   ))''') # Credit to https://ascii.co.uk/art/clouds
    elif("Mostly Sunny" in forecast):
        print('''
    ,--.:::::::::::::::::::::::::::::....:::::::
        ):::::::::::::::::::::::::..      ..::::
      _'-. _::::::::::::::::::::..   ,--.   ..::
     (    ) ),--.:::::::::::::::.   (    )   .::
                 )-._:::::::::::..   `--'   ..::
    _________________)::::::::::::..      ..::::''') # Credit: https://ascii.co.uk/art/clouds
    elif((forecast == "Cloudy") or (forecast == "Mostly Cloudy")):
        print('''
                    ███████████            
                  ██          ████          
                ██              ▒▒██        
            ████▒▒                ██        
      ██████      ▒▒            ▒▒▒▒████    
    ██▒▒            ▒▒        ▒▒      ▒▒██  
    ██▒▒▒▒           ▒▒▒▒▒▒▒▒▒          ▒▒██
      ████████████████████████████████████  ''') # Credit: https://textart.sh/topic/cloud
    elif(forecast == "Sunny"):
        print('''
                      ,
                      :
         '.        _______       .'
           '  _.-"`       `"-._ '
            .'                 '.
     `'--. /                     \\ .--'`
          /                       \\
      '   |                       |  '-.''')
    elif("clear" in forecast.lower()):
        print('''
    --------------------------------
    --------------------------------
    -------------------- ________ --
    --------------- ____/ +      \\__
    -------------- (       -
    ---- _________/    *      =
    ____/    `     @             :''')
    elif(("rain/snow" in forecast.lower()) or ("sleet" in forecast.lower())):
        print('''
                      ██████            
                    ██      ████      
              ████▒▒           ███   
           ██▒▒    ▒▒        ▒▒   ▒▒██
         ██         ▒▒▒▒▒▒▒▒▒▒      ▒▒██
        █████████████████████████████████
           i  * i  * i  * i    i*   *
         *   i  * i  * i  *  i *   i  *   ''')
    elif((("showers" in forecast.lower()) or ("shower" in forecast.lower()) or ("drizzle" in forecast.lower())) and ("slight" not in forecast.lower()) and ("snow" not in forecast.lower())):
        print('''
                      ██████            
                    ██      ████      
              ████▒▒           ███   
           ██▒▒    ▒▒        ▒▒   ▒▒██
         ██         ▒▒▒▒▒▒▒▒▒▒      ▒▒██
        █████████████████████████████████ 
           i    i    i     i      i 
             i    i   i   i     i   ''')
    elif(("snow" in forecast.lower()) or ("snow shower" in forecast.lower())):
        print('''
                      ██████            
                    ██      ████      
              ████▒▒           ███   
           ██▒▒    ▒▒        ▒▒   ▒▒██
         ██         ▒▒▒▒▒▒▒▒▒▒      ▒▒██
        █████████████████████████████████ 
           *    *    *     *      * 
         *    *    *    *      *    *    ''')
    elif(("rain" in forecast.lower()) and not ("slight" in forecast.lower()) and not ("shower" in forecast.lower())):
        print('''
              0      00  000000000000
             0000 0  0000000000000000000
      000000000000000000000000000000000000
   000000000000000000000000000000000000000000
       0000000000000000000000000000000
          / / / / / / / / / / / / /
        / / / / / / / / / / / /
        / / / / / / / / / /''') # Credit: https://www.asciiart.eu/nature/rains
    elif((forecast == "Slight Chance Rain Showers") or (forecast == "Slight Chance Showers And Thunderstorms")):
        print('''
                    ███████████            
                  ██          ████          
                ██              ▒▒██        
            ████▒▒                ██        
      ██████      ▒▒            ▒▒▒▒████    
    ██▒▒            ▒▒        ▒▒      ▒▒██  
    ██▒▒▒▒           ▒▒▒▒▒▒▒▒▒          ▒▒██
      ████████████████████████████████████  ''') # Credit: https://textart.sh/topic/cloud
    elif("fog" in forecast.lower()):
        print('''
    ---///---///---///---///---///---///
    ///-ffffff//-ooooooo/--gggggg-///---
    ---/fff--///-o-///-o-//g---/g/---///
    ///-ffffff--/o/-o-/o/--gggggg-///---
    ---/fff--///-o-///-o-///---/g/---///
    ///-fff//---/ooooooo/--gggggg-///---
    ---///---///---///---///---///---///''')
    else:
        # First we have to find the characters in the longest word, then center it approprietally.
        # This is what i'm planning (this is a placeholder if the forecast isn't recognized):
        '''
            +-------------+
            | M o s t l y |
            |  S u n n y  |
            +-------------+
        '''
        # First! Calculate the amount of letters in the longest word. This will be needed
        # to center the text.
        words = forecast.split(" ")
        letters = 0
        for i in words:
            if(len(i) > letters):
                letters = len(i)

        # Now we need to compoute exactly how many dashes we will need on the top row.
        # That is, the letters multiplied by two and then add two for padding.
        dashCount = letters * 2 + 2

        # Now let's draw the top line.
        sys.stdout.write("\n        +")
        for i in range(1, dashCount):
            sys.stdout.write("-")
        sys.stdout.write("+\n")

        # Cool! Now let's get into the meat and potatoes of this. Repeat this next thing for every word.
        for i in words:
            # Starting stuffs
            sys.stdout.write("        | ")

            # We need to find out how many spaces to put in front to space things out. We
            # can do this by making use of our old letters variable.
            spaces = letters - len(i)
            for j in range(0, spaces):
                sys.stdout.write(" ")
            
            # Finally start printing out letters and spaces
            inc = 0
            for j in i:
                if(inc == letters):
                    sys.stdout.write(j)
                else:
                    sys.stdout.write(j + " ")
                inc += 1
            
            # Now we need to add spaces again.
            for j in range(0, spaces):
                sys.stdout.write(" ")
            
            # Finish up
            sys.stdout.write("|\n")
        
        # Do the last line of dashes
        sys.stdout.write("        +")
        for i in range(1, dashCount):
            sys.stdout.write("-")
        sys.stdout.write("+\n")

def main():
    try:
        # Let the log know that main.py was started properly.
        log("Displayer Started.")

        # Establish a message channel with getter
        log("Creating/Clearing Communications File...")
        with open("passthru", "w") as comms:
            comms.write("")

        # Do this with text outputed. We'll do this again without text on the screen later.
        if(os.path.exists("weatherCache.json") == True):
            log("weatherCache.json still exists. Making it a backup...")
            os.rename("weatherCache.json", "weatherCache-bk.json")
        if(os.path.exists("hourWeatherCache.json") == True):
            log("hourWeatherCache.json still exists. Making it a backup...")
            os.rename("hourWeatherCache.json", "hourWeatherCache-bk.json")
        while(True):
            with open("passthru", "r") as comm:
                comms = comm.read()
            
            # Check for various getter messages
            if("OUTDATE" in comms):
                # We've found out that the data we got is out of data, and we have no backups!
                # Display something!
                log("Recieved Out of Date Message")
                os.system("cowsay -d \"Inaccurate Data\"")
                sleep(300)
            if("nourl" in comms):
                # There is no URL File
                log("Recieved No URL Message...")
                print("\nERROR: Could not find the NWS Destination URL!")
                print("If this is your first time running the script, you may have not\nput in the \
destination URL. If you don't know how to do this,\ngo to https://github.com/JR-Tech-and-Software/Weather-Displayer\n\
and read the README.md file to explain the steps to do this.")
                sleep(5)
                return 1

            if(os.path.exists("weatherCache.json") == False):
                print("Waiting for data...")
                sleep(0.5)
            else:
                # Data recieved. Let the log know!
                log("Recieved JSON. Ready to display...")
                break

        # This ENTIRE thing should be repeated
        while(True):
            # Get our json data from files

            while(True):
                try:
                    with open("weatherCache.json", "r") as theData:
                        data = json.load(theData)
                    with open("hourWeatherCache.json", "r") as theData:
                        hourData = json.load(theData)
                    break
                except json.decoder.JSONDecodeError as e:
                    print("Couldn't read JSON data. Trying Again...", e)
                    log("Couldn't decode the JSON. Trying again. Next few lines contain error information.")
                    log(str(e))
                    sleep(1)
            
            # Now time for the meat and potatoes of this script: Displaying weather data
            os.system("clear")

            # Get decoded data in arrays using functions above
            log("Decoding JSON Data...")
            currentTemps = decodeTemps(data)
            tempUnits = decodeTempUnit(data)
            titles = decodeTitles(data)
            forecasts = decodeForecasts(data)
            windSpeed = decodeWindSpeed(hourData)
            windDir = decodeWindDir(hourData)
            hourForecast = decodeForecasts(hourData)
            nowTemp = decodeTemps(hourData)

            #for i in range(0,4):
            #    print(titles[i] + ": " + forecasts[i] + ". Temp: " + str(currentTemps[i]) + "°" + tempUnits[i])
            
            # Print out display art
            log("Printing out display...")
            artDisplay(hourForecast[0])
            print("        ", hourForecast[0])
            print("Current Temperature:", str(nowTemp[0]) + ",",
                    titles[1] + "'s Temperature:\n" + str(currentTemps[1]) + ",",
                    titles[2] + "'s Temperature:", str(currentTemps[2]))
            print("The wind:", windDir[0], "at", windSpeed[0] + ".")

            log("Display has completed. Time to manage JSON files then wait.")

            # We now need to clear all cached files so that we can update it again.
            # To do this, we'll simply make backup files (so that in the case there)
            # is no internet to download, we can simply use those.
            if(os.path.exists("weatherCache.json") == True):
                if(os.path.exists("weatherCache-bk.json") == True):
                    log("Previous long-term backups exist! Deleting them to ensure no confusion")
                    os.remove("weatherCache-bk.json")
                os.rename("weatherCache.json", "weatherCache-bk.json")
                log("Transfering JSON files to backup...")
            if(os.path.exists("hourWeatherCache.json") == True):
                if(os.path.exists("hourWeatherCache-bk.json") == True):
                    log("Previous hourly backups exist! Deleting them to ensure no confusion")
                    os.remove("hourWeatherCache-bk.json")
                os.rename("hourWeatherCache.json", "hourWeatherCache-bk.json")
                log("Transfering Hourly JSON files to backup...")
            i = 0
            while(True):
                if(os.path.exists("weatherCache.json") == False):
                    sleep(0.5)
                    if((i > 3600) and (i < 3603)):
                        log("Still waiting for JSON Data. Hasn't been recieved in a long time.")
                        print("Weather info hasn't updated in a while. Try restarting the system.\nIf problems presist, check the log.")
                else:
                    log("New JSON recieved. Starting the cycle again.")
                    break
                i += 1
    except KeyboardInterrupt:
        # Final things to be done
        file = open("passthru", "w")
        file.write("don")
        file.close()
        log("Interrupt signal recieved. Sending Quit Signal...")
        print("WAIT! Quitting getter script...")
        sleep(1)
        file = open("passthru", "w")
        file.write("")
        file.close()
        log("Done sending quit signals. Quitting.")
        return 0

if(__name__ == "__main__"):
    exit(main())