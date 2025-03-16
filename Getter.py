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