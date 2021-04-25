import requests, json
from datetime import datetime
#variables
base_url = "http://api.openweathermap.org/data/2.5/onecall?"
lat = "32.9483"
lon = "-96.7299"
complete_url = base_url + "lat=" + lat + "&lon=" + lon + "&exclude=daily" + "&appid=" + api_key + "&units=imperial"

#Pull in current weather data
response = requests.get(complete_url)
weatherData = response.json()
#check if city is found -> get current temperature
if weatherData["lat"] != "404":
    current = weatherData["current"]
    current_temperature = current["temp"]
    current_humidity = current["humidity"]
    current_time = current["dt"]
    hourly = weatherData["hourly"]
    nexthour = hourly[1]
    nexthr_temp = nexthour["temp"]
    nexthr_humidity = nexthour["humidity"]

    # print following values
    '''
    print(datetime.utcfromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S'))
    
    print(  "Temperature  = " +
        str(current_temperature) +
        "\n Humidity = " + 
        str(current_humidity))

    print(" Next hour's temperature  = " +
                str(nexthr_temp) +
                "\n Next hour's Humidity = " + 
                str(nexthr_humidity))
    '''

    f = open('operating_values/outside_temp.csv','w')
    f.write(str(current_temperature))
    f.close()

else:
    print(" ERROR IN FETCHING WEATHER DATA ")


#check desired temprature

#either turn on A/C or Heat based on desired tmeprrature

#Write to report periodically
#Current Time | Current Temperature | Desired Temperature
