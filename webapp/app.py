from flask import Flask, render_template, redirect, request
import requests, json

from datetime import datetime

#variables
api_key = ""
base_url = "http://api.openweathermap.org/data/2.5/onecall?"
lat = "32.95"
lon = "-96.73"
complete_url = base_url + "lat=" + lat + "&lon=" + lon + "&exclude=daily" + "&appid=" + api_key + "&units=imperial"

app = Flask(__name__)

with open("../operating_values/goal_temp.csv", "r") as f:
    goal = f.read()

with open("../operating_values/room_temp.csv", "r") as f:
    room = f.read()

with open("../operating_values/outside_temp.csv", "r") as f:
    out = f.read()

with open("../operating_values/hvac.csv", "r") as f:
	op = f.readline()
	ops = f.readline().split(',')
	if ops[0] == "0":
		fan = "Off"
	else:
		fan = "On"
	if ops[1] == "0":
		heat = "Off"
	else:
		heat = "On"
	if ops[2] == "0":
		ac = "Off"
	else:
		ac = "On"

@app.route('/')
def control():
    return render_template('control.html', setTo=goal, inside=room, outside=out, fanStatus=fan, acStatus=ac, heatStatus=heat)

#background process happening without any refreshing
@app.route('/tempup')
def tempup():
	print ("temp go up")
	#read current temp and write increased
	f = open("../operating_values/goal_temp.csv", "r")
	x = int(f.read())
	f.close()
	x = x + 1
	current = x
	f = open("../operating_values/goal_temp.csv", "w")
	f.write(str(x))
	f.close()
	f = open("../operating_values/room_temp.csv", "r")
	y = f.read()
	f.close()
	f = open("../operating_values/outside_temp.csv", "r")
	z = f.read()
	f.close()

	return render_template('control.html', setTo=x, inside=y, outside=z, fanStatus=fan, heatStatus=heat, acStatus=ac)

@app.route('/tempdown')
def tempdown():
	print ("temp go down")
	#read current temp and write increased
	f = open("../operating_values/goal_temp.csv", "r")
	x = int(f.read())
	f.close()
	x = x - 1
	current = x
	f = open("../operating_values/goal_temp.csv", "w")
	f.write(str(x))
	f.close()
	f = open("../operating_values/room_temp.csv", "r")
	y = f.read()
	f.close()

	f = open("../operating_values/outside_temp.csv", "r")
	z = f.read()
	f.close()

	return render_template('control.html', setTo=x, inside=y, outside=z, fanStatus=fan, heatStatus=heat, acStatus=ac)

@app.route('/update')
def update():
	print ("update values")
	f = open("../operating_values/goal_temp.csv", "r")
	x = int(f.read())
	f.close()
	f = open("../operating_values/room_temp.csv", "r")
	y = f.read()
	f.close()

	f = open("../operating_values/outside_temp.csv", "r")
	z = f.read()
	f.close()

	with open("../operating_values/hvac.csv", "r") as f:
		op = f.readline()
		ops = f.readline().split(',')
		if ops[0] == "0":
			fan = "Off"
		else:
			fan = "On"
		if ops[1] == "0":
			heat = "Off"
		else:
			heat = "On"
		if ops[2] == "0":
			ac = "Off"
		else:
			ac = "On"

	return render_template('control.html', setTo=x, inside=y, outside=z, fanStatus=fan, heatStatus=heat, acStatus=ac)

if __name__ == '__main__':
	app.run(debug=True, host = '0.0.0.0')
