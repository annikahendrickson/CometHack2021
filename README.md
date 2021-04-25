# CometHack2021: EcoStat

## Inspiration

With Earth day having been so recently, we knew we wanted to do a project that could benefit our environment. We also drew inspiration from Texas' (recently) lacking energy infrastructure and the cause for its failure: high energy demand for heating homes. Putting this together, we came up with the idea of EcoStat, a thermostat that learns to save energy.

## What it does

The EcoStat smart thermometer actively monitors the R-value (thermal resistance) of your apartment to promote greener habits. It is also interfaced with our web application to remotely control the temperature, as well as to monitor the operations of the HVAC unit. It displays the R-value over time for the day and for the week such that the user can understand how their schedules affect their power consumption.

## How we built it

By wiring a Raspberry Pi to a 4-channel relay, we were able to control the 24V switching of the thermostat with the 5V main from the Pi. Further, by creating a 3 compartment model for heat flow, we were able to predict the future temperature of the apartment when combining the data from the onboard thermometer along with openWeather's API. With this, we used gradient descent to determine the instantaneous R-value between the apartment and the environment, and we saved and plotted these with matplotlib.

## Accomplishments that we're proud of

Building a thermometer! Getting javascript to work after so many long hours. Learning python and flask as many of us had no experience. Overcoming network issues and seemingly impossible hardware problems.

## What we learned

Placing 20 V 20mA over a measly single 5 Ohm resistor will likely result in smoke. BJTs and weak MOSFETs will break down too. Electromechanical switches are certainly preferable for high power systems. 

## What's next for EcoStat

We spent probably 12 hours attempting to develop our own node.JS plugin such that our thermostat could interface with Apple's Homekit, so we'll likely continue work on this goal. Additionally, we'd like to continue to improve our mathematical models.
