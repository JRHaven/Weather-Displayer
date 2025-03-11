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
from main import artDisplay
import flask, os, requests, json, time, threading, logging, Logger

# We're going to need to create a start-time variable to calculate uptime for logging purposes
startTime = time.time()

# Use right logging library to reconfigure Flask logs
flaskLogger = logging.getLogger('werkzeug')
flaskLogger.setLevel(logging.CRITICAL)

# Global weather data variables
data = ""
hourData = ""

# Global logger
logger = None

# Initialize Dirs
def initDirs():
    if(not os.path.exists("static")):
        log("Directories don't exist, creating directories and contents (css, html, etc.)")
        os.mkdir("static")
        os.mkdir("templates")

        # Change permissions (meant to be run as sudo)
        os.chmod("static", 0o777)
        os.chmod("templates", 0o777)

        with open("static/style.css", "w") as css:
            css.write("""\
/*
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
*/

* {
    text-align: center;
    align-content: center;
    align-items: center;
}

div {
    padding-left:1%;
    padding-right:1%;
    padding-top:0.25%;
    padding-bottom:0.25%;
    outline:3px black solid;
    margin: 5px;
}

div#outlook{
    padding-top:0px;
    padding-bottom:0px;
    display:flex;
}

div#future{
    outline:none;
    padding-left:2%;
    padding-right:2%;
    vertical-align:center;
    width:21%;
    margin:0px;
}

div#horr-future{
    outline:none;
    padding-top:2%;
    padding-bottom:2%;
    vertical-align:center;
    margin:0px;
}

div#divider{
    height:200px;
    width:1px;
    background-color:rgb(181, 181, 181);
    outline:0px;
    padding:1px;
}

div#horr-divider{
    width:200px;
    height:1px;
    background-color:rgb(181, 181, 181);
    outline:none;
    padding:1px;
}

div#header{
    outline:none;
    color:white;
    background-color: black;
    margin-left:25%;
    margin-right:25%
}

div#current-conditions{
    padding-left:10%;
    padding-right:10%;
}

div#inline{
    outline:none;
    vertical-align: center;
    display:flex;
}

div#image{
    outline:none;
    margin-left:30%;
}

h3#temp{
    font-size:18pt;
}

h4#temp{
    font-size:14pt;
    margin-top:0px;
}

small#inH{
    font-size:10pt;
}

div#fullOutlook{
    padding-top:0px;
    padding-bottom:0px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
}

h2#currentForecast{
    padding-left:5%;
}

div#fullCenter{
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    outline:none;
}

div#header a:visited{
    color:white;
}

div#header a{
    color:white;
}

pre{
    text-align:left;
}
""")
            css.close()
        os.chmod("static/style.css", 0o777)
        with open("templates/template.htm", "w") as html:
            html.write("""\
<!--
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
-->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
    <title>NWS Weather</title>
    <meta http-equiv="refresh" content="900">
</head>
<body>
    <div id="header">
        <h1>Current NWS Weather</h1>
        <small>Visit <a href="https://www.weather.gov">the official NWS website</a> for more information.</small>
    </div>
    <br>
    <div id="current-conditions">
        <div id="inline">
            <div id="image">
                <pre>{{ currentWeather[5] }}</pre>
                <h2 id="currentForecast">{{ currentWeather[0] }}</h2>
            </div>
            <h3 id="temp">{{ currentWeather[1] }}&deg;{{currentWeather[2]}}</h3>
        </div>
        <p>
            {{currentWeather[3]}}
        </p>
    </div>
    <br>
    <div id="outlook">
        {% for i in range(0,4) %}
        <div id="future">
            <h3>{{ title[i] }}</h3>
            {% if shortDesc[i].split(" ")|length > 3 %}
            <h4 style="padding-bottom:0.5%">{{ shortDesc[i] }}</h4>
            {% elif shortDesc[i].split(" ")|length > 7 %}
            <h4 style="padding-bottom:0.25%">{{ shortDesc[i] }}</h4>
            {% else %}
            <h4>{{ shortDesc[i] }}</h4>
            {% endif %}
            <h4 id="temp">{{ temp[i] }}&deg;{{currentWeather[2]}}</h4>
            <p>
                {{ longDesc[i] }}
            </p>
        </div>
        {% if i < 3 %}
        <div id="divider"></div>
        {% endif %}
        {% endfor %}
    </div>

    <div id="fullCenter"><p><a href="{{ url_for('fullForecast') }}">Show Full Forecast</a> | <a href="{{ url_for('hourly') }}">Show Hourly Forecast</a></p></div>
</body>
</html>""")
            html.close()
        os.chmod("templates/template.htm", 0o777)
        with open("templates/allinfo.htm", "w") as html:
            html.write("""\
<!--
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
-->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/style.css">
    <title>NWS Weather: Full Forecast</title>
    <meta http-equiv="refresh" content="900">
</head>
<body>
    <div id="header">
        <h1>Full NWS Forecast</h1>
        <small>Visit <a href="https://www.weather.gov">the official NWS website</a> for more information.</small>
    </div>
    <br>
    <br>
    <div id="fullOutlook">
        {% for i in range(0,title|length) %}
        <div id="horr-future">
            {% if title[i] != "" %}
            <h3>{{ title[i] }}</h3>
            {% else %}
            <h3>Hour {{i}}</h3>
            {% endif %}

            {% if shortDesc[i].split(" ")|length > 3 %}
            <h4 style="padding-bottom:0.5%">{{ shortDesc[i] }}</h4>
            {% elif shortDesc[i].split(" ")|length > 7 %}
            <h4 style="padding-bottom:0.25%">{{ shortDesc[i] }}</h4>
            {% else %}
            <h4>{{ shortDesc[i] }}</h4>
            {% endif %}
            <h4 id="temp">{{ temp[i] }}&deg;{{unit}}</h4>
            <p>
                {% if longDesc[i] != "" %}
                {{ longDesc[i] }}
                {% endif %}
            </p>
        </div>
        {% if i < title|length - 1 %}
        <div id="horr-divider"></div>
        {% endif %}
        {% endfor %}
        <a href="{{ url_for('display') }}">Show Full Forecast</a>
    </div>
</body>
</html>""")
            html.close()
        os.chmod("templates/allinfo.htm", 0o777)


def getJSON():
    # Use global variables
    global data, hourData

    # Get our json data from files (code stolen from main.py)
    attmpt = 0
    while(True):
        try:
            if(os.path.exists("weatherCache.json")):
                try:
                    with open("weatherCache.json", "r") as theData:
                        data = json.load(theData)
                        theData.close()
                    log("Was able to load fresh general data.")
                except FileNotFoundError:
                    log("General Data File Vanished! Trying again after 0.5 secs...")
                    sleep(0.5)
                    attmpt += 1
                    if(attmpt > 5):
                        log("Attempt Timeout achieved, will wait 5 minutes to continue.")
                        sleep(300)
                        attmpt = 0
                    continue
            elif(os.path.exists("weatherCache-bk.json")):
                try:
                    with open("weatherCache-bk.json", "r") as theData:
                        data = json.load(theData)
                        theData.close()
                    log("Got general weather from backup.")
                except FileNotFoundError:
                    log("General Data Backup Vanished! Trying again after 0.5 secs...")
                    sleep(0.5)
                    attmpt += 1
                    if(attmpt > 5):
                        log("Attempt Timeout achieved, will wait 5 minutes to continue.")
                        sleep(300)
                        attmpt = 0
                    continue
            else:
                # Unable to get JSON, must not be provided from main.py yet
                log("General weather info unavailble. Will try again after 0.5 seconds.")
                sleep(0.5)
                continue
            break
        except json.decoder.JSONDecodeError as e:
            log("Couldn't decode the JSON. Trying again. Next few lines contain error information.")
            log(str(e))
            sleep(1)

    attmpt = 0
    while(True):
        try:
            if(os.path.exists("hourWeatherCache.json")):
                try:
                    with open("hourWeatherCache.json", "r") as theData:
                        hourData = json.load(theData)
                        theData.close()
                    log("Was able to get fresh hourly data.")
                except FileNotFoundError:
                    log("Hourly Data File Vanished! Trying again after 0.5 secs...")
                    sleep(0.5)
                    attmpt += 1
                    if(attmpt > 5):
                        log("Attempt Timeout achieved, will wait 5 minutes to continue.")
                        sleep(300)
                        attmpt = 0
                    continue
            elif(os.path.exists("hourWeatherCache-bk.json")):
                try:
                    with open("hourWeatherCache-bk.json", "r") as theData:
                        hourData = json.load(theData)
                        theData.close()
                    log("Got hourly weather from backup.")
                except FileNotFoundError:
                    log("Hourly Backup File Vanished! Trying again after 0.5 secs...")
                    sleep(0.5)
                    attmpt += 1
                    if(attmpt > 5):
                        log("Attempt Timeout achieved, will wait 5 minutes to continue.")
                        sleep(300)
                        attmpt = 0
                    continue
            else:
                log("Hourly weather info unavalible. Will try again after 0.5 seconds.")
                sleep(0.5)
                continue
            break
        except json.decoder.JSONDecodeError as e:
            log("Couldn't decode the JSON. Trying again. Next few lines contain error information.")
            log(str(e))
            sleep(1)
    
    # Return in an array. Index 0 is general, index 1 is hourly.
    return [data, hourData]

# Flask things
initDirs()
iamweb = flask.Flask(__name__, static_folder="static", template_folder="templates")

# Initialize/Update JSON, Image
def getInfo():
    global data, hourData, logger
    # Get JSON
    logger.log("WEB      ", "Getting weather info...")
    jsonData = getJSON()
    data = jsonData[0]
    hourData = jsonData[1]

# Get various values
def getShortForecasts(data):
    periods = data["properties"]["periods"]
    forecasts = []
    for i in periods:
        forecasts.append(i["shortForecast"])
    return forecasts
def getTemps(data):
    periods = data["properties"]["periods"]
    forecasts = []
    for i in periods:
        forecasts.append(i["temperature"])
    return forecasts
def getDetailForecasts(data):
    periods = data["properties"]["periods"]
    forecasts = []
    for i in periods:
        forecasts.append(i["detailedForecast"])
    return forecasts
def getTitles(data):
    periods = data["properties"]["periods"]
    forecasts = []
    for i in periods:
        forecasts.append(i["name"])
    return forecasts

@iamweb.route("/")
def display():
    # Use global weather data, logger
    global data, hourData, logger
    logger.log("WEB      ", "Displaying main forecast page")
    currentWeather = [data["properties"]["periods"][0]["shortForecast"], hourData["properties"]["periods"][0]["temperature"], hourData["properties"]["periods"][0]["temperatureUnit"], data["properties"]["periods"][0]["detailedForecast"],\
        artDisplay(data["properties"]["periods"][0]["shortForecast"])]
    return flask.render_template("template.htm", currentWeather=currentWeather, title=getTitles(data), shortDesc=getShortForecasts(data),\
        temp=getTemps(data), longDesc=getDetailForecasts(data))

@iamweb.route("/full")
def fullForecast():
    # Only use general data - use global variable, as well as logger
    global data, logger
    logger.log("WEB      ", "Displaying full forecast page")
    return flask.render_template("allinfo.htm", title=getTitles(data), shortDesc=getShortForecasts(data), temp=getTemps(data),\
        longDesc=getDetailForecasts(data), unit=hourData["properties"]["periods"][0]["temperatureUnit"])

@iamweb.route("/hourly")
def hourly():
    # Only use hourly data - use global variable, as well as logger
    global hourlData, logger
    logger.log("WEB      ", "Displaying hourly page")
    return flask.render_template("allinfo.htm", title=getTitles(hourData), shortDesc=getShortForecasts(hourData), temp=getTemps(hourData),\
        longDesc=getDetailForecasts(hourData), unit=hourData["properties"]["periods"][0]["temperatureUnit"])

def main(port, mainLogger: Logger):
    # Register logger
    global logger
    logger = mainLogger
    
    # Get our things
    initDirs()
    getInfo()

    # Run flask in a seperate thread
    logger.log("WEB      ", "Creating and starting Flask thread with Debug false, host 0.0.0.0, port" + str(port) + ", and no reloader...")
    flaskThread = threading.Thread(target=iamweb.run, kwargs={"debug":False, "host":"0.0.0.0", "port":port, "use_reloader":False})
    flaskThread.start()

    # Loop to change info every 15 minutes
    while(True):
        sleep(900)
        getInfo()
