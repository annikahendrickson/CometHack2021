import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#takes input values of current temp and goal temp and determines how to run the AC unit
def thermostat_control(room_temp_f,goal_temp_f,tolerance,ac_mode=-1):
    fan = 0
    heat = 0
    ac = 0
    if ac_mode == -1:
        if goal_temp_f > out_temp_f:
            ac_mode = 0
    else:
        ac_mode = 1

    if not ac_mode:
        if room_temp_f<goal_temp_f-tolerance:
            fan = 1
            heat = 1
            ac = 0
        if room_temp_f>goal_temp_f+tolerance:
            fan = 0
            heat = 0
            ac = 0

    if ac_mode:
        if room_temp_f<goal_temp_f-tolerance:
            fan = 0
            heat = 0
            ac = 0
        if room_temp_f>goal_temp_f+tolerance:
            fan = 1
            heat = 0
            ac = 1
    return fan,heat,ac
#3 compartment model between room, hvac, and outside reservoir
def interate_heat(room_heat,hvac_heat,room_temp_k,hvac_temp_k,R1,R2,t_step,fan,heat,ac):
    dQ_heat = (heat_power/3600)*t_step
    dQ_ac = (ac_power/3600)*t_step

    if heat:
        hvac_heat=hvac_heat+dQ_heat
    if ac:
        hvac_heat=hvac_heat-dQ_ac
    if fan:
        R2 = R2_fan
    else:
        R2 = R2_no_fan

    dQ_out_room = (1/R1)*(out_temp_k - room_temp_k)*t_step #kJ
    dQ_room_hvac = (1/R2)*(room_temp_k - hvac_temp_k)*t_step #kJ

    room_heat = room_heat + dQ_out_room - dQ_room_hvac #kJ
    hvac_heat = hvac_heat + dQ_room_hvac #kJ
    return room_heat,hvac_heat

#converts farenheit to kelvin
def f_to_k(temp):
    return (5/9 * (temp - 32)) + 273.15
def k_to_f(temp):
    return ((temp - 273.15) * 9/5) + 32
#defining arduino pin numbers for relay
fan_pin = 11
ac_pin = 8
heat_pin = 9

#initializing control system variables
fan = 0
ac = 0
heat = 0
tolerance = 0.1

#sets up arduino pins for later use
GPIO.setmode(GPIO.BCM)
GPIO.setup(fan_pin, GPIO.OUT)
GPIO.setup(ac_pin, GPIO.OUT)
GPIO.setup(heat_pin, GPIO.OUT)
GPIO.output(fan_pin, fan)
GPIO.output(ac_pin, ac)
GPIO.output(heat_pin, heat)
dhtDevice = adafruit_dht.DHT22(board.D4)

#sets time variables
duration = 0
start_time = time.time()
prev_time = start_time
old_update_time = start_time
update_time = start_time


#experimentally determined values 
ac_power = 928.58 #kJ/hr
heat_power = 5000 #kJ/hr
room_capacity = 123 #kJ/K
hvac_capacity = 10 #kJ/K #sum must be 133
R1 = 35 # K/kJ*sec
R2_fan = 10 # K/kJ*sec
R2_no_fan = 20 # K/kJ*sec

#initializes heat measurements for room and hvac system
room_temp_c = 0
while room_temp_c == 0:
    try:
        room_temp_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
    except Exception as error:
        time.sleep(1)
        break
room_temp_k = room_temp_c + 273.15
hvac_temp_k = room_temp_k
room_heat = room_temp_k*room_capacity #kJ
hvac_heat = hvac_temp_k*hvac_capacity #kJ
hvac_temp_f = k_to_f(hvac_temp_k)
old_update_hvac_temp_f = hvac_temp_f
old_hvac_temp_f = hvac_temp_f

#initializes value for previous room temperature
old_room_temp_f = 0
old_update_room_temp_f = 0
t_list = []
ac_list = []
heat_list = []
fan_list = []
while True:
    try:
        #resets update boolean
        update = False

        #gets outside temp and goal temp from csv files
        goal_temp_f = float(np.genfromtxt('operating_values/goal_temp.csv', delimiter=','))
        out_temp_f = float(np.genfromtxt('operating_values/outside_temp.csv', delimiter=','))+4

        #gets current room temp data from sensor
        room_temp_c = dhtDevice.temperature
        room_temp_k = room_temp_c + 273.15
        room_temp_f = room_temp_c * (9/5) + 32

        #converts all other values to Kelvin
        goal_temp_k = f_to_k(goal_temp_f)
        out_temp_k = f_to_k(out_temp_f)


        #gets current time and calculated runtime and time between update
        current_time = time.time()
        duration = current_time - start_time
        t_step = current_time - prev_time 
        t_list.append(t_step)
        prev_time = current_time

        #checks to see if measured temperature changed
        if room_temp_f != old_room_temp_f:
            simulate_list = [t_list,fan_list,heat_list,ac_list]
            t_list = []
            fan_list = []
            heat_list = []
            ac_list = []
            update = True
            old_update_room_temp_f = old_room_temp_f
            old_update_hvac_temp_f = old_hvac_temp_f
            old_hvac_temp_f = hvac_temp_f
            old_update_time = update_time
            update_time = time.time()
            update_duration = update_time-old_update_time

        old_room_temp_f = room_temp_f

        #ac_mode enable, and returns appropriate control variables
        ac_mode = 1
        fan,heat,ac = thermostat_control(room_temp_f,goal_temp_f,tolerance,ac_mode)
        
        fan_list.append(fan)
        heat_list.append(heat)
        ac_list.append(ac)

        #switches or unswitches various pins to control hvac system
        GPIO.output(fan_pin, fan)
        GPIO.output(ac_pin, ac)
        GPIO.output(heat_pin, heat)

        p_room_temp_k = room_heat/room_capacity 
        hvac_temp_k = hvac_heat/hvac_capacity 
        #updates heat based off of current values    
        room_heat,hvac_heat = interate_heat(room_heat,hvac_heat,p_room_temp_k,hvac_temp_k,R1,R2_fan,t_step,fan,heat,ac)

        #calculates temperatures from heat
        p_room_temp_k = room_heat/room_capacity 
        hvac_temp_k = hvac_heat/hvac_capacity 
        p_room_temp_f = k_to_f(p_room_temp_k) 
        hvac_temp_f = k_to_f(hvac_temp_k)


        #when new sensor value released, calculate the error in R value measurement
        if update and duration > 1:
            
            #alpha learning rate
            alpha = 0.01
            #threshold for minimum
            threshold = 1e-5
            #print(old_update_room_temp_f,room_temp_f,old_update_hvac_temp_f,hvac_temp_f,update_duration)
            slope = 1
            R_old = R1
            while abs(slope) > threshold and R1 < 1000:
                simulated_room_temp_k = f_to_k(old_update_room_temp_f)
                simulated_hvac_temp_k = f_to_k(old_update_hvac_temp_f)
                simulated_room_heat = simulated_room_temp_k*room_capacity
                simulated_hvac_heat = simulated_hvac_temp_k *hvac_capacity

                dR1 = 0.001
                error_i = room_temp_f-p_room_temp_f
                R_test=R1+dR1
                for i in range(len(simulate_list[0])):
                    sim_t = simulate_list[0][i]
                    s_fan = simulate_list[1][i]
                    s_heat = simulate_list[2][i]
                    s_ac = simulate_list[3][i]

                    simulated_room_heat,simulated_hvac_heat = interate_heat(simulated_room_heat,simulated_hvac_heat,simulated_room_temp_k,simulated_hvac_temp_k,R_test,R2_fan,sim_t,s_fan,s_heat,s_ac)
                    simulated_room_temp_k = simulated_room_heat/room_capacity
                    simulated_hvac_temp_k = simulated_hvac_heat/hvac_capacity
                simulated_room_temp_f = k_to_f(simulated_room_temp_k)
                error_f = room_temp_f-simulated_room_temp_f
                dE = error_f-error_i
                slope = (dE/dR1)
                #print('Slope:',slope,'R1:',(R1 - alpha*(dE/dR1)))#,'E_i:',error_i,'E_f:',error_f)
                #print(slope)
                R1 = R1 + alpha*slope

            if slope >= 1000:
                R1 = R_old
                print('diverged')
            print('Updated R1:',str(R1))
            p_room_temp_f = room_temp_f
            hvac_temp_f = room_temp_f

            now = datetime.now()

            hour = int(now.strftime("%-H"))
            minute = int(now.strftime("%-M"))
            sec = int(now.strftime("%-S"))

            my_time = hour + minute/60 + sec/3600

            my_day = ((datetime.today().weekday()+1)%7)+1

            f = open('operating_values/run_history.csv','a')
            f.write(str(my_day)+','+str(round(my_time,5))+','+str(R1)+','+str(room_temp_f)+'\n')
            f.close()

            #history = np.genfromtxt('operating_values/run_history.csv', delimiter=',')
            df = pd.read_csv('operating_values/run_history.csv', usecols= ['day','time','R','T'])
            days = df['day']
            ts = df['time']
            Rs = df['R']
            Ts = df['T']
            d_avg = range(1,7)
            R_avg = []
            T_avg = []
            for i in range(1,7):
                R_sum = 0
                T_sum = 0
                counts = 0
                for j in range(len(days)):
                    if days[j] == i:
                        R_sum += Rs[j]
                        T_sum += Ts[j]
                        counts += 1
                if counts != 0:
                    R_avg.append(R_sum/counts)
                    T_avg.append(T_sum/counts)
                else:
                    R_avg.append(0)
                    T_avg.append(0)

            '''
            figure = plt.figure()
            graph = figure.add_subplot(111)
            graph.plot(ts,Rs,'-',c='red')
            graph.plot(ts,Ts,'-',c='blue')
            red_patch = mpatches.Patch(color='red', label='R-Value')
            blue_patch = mpatches.Patch(color='blue', label='Temp')
            plt.legend(handles=[blue_patch,red_patch])
            graph.set_xlabel('Time since Midnight (hours)')
            graph.set_ylabel('Temperature (F)')
            plt.savefig('webapp/static/graph1.png')
            '''

            fig, ax1 = plt.subplots()

            ax2 = ax1.twinx()

            ax1.plot(ts, Ts, 'r-')
            ax2.plot(ts, Rs, 'b-')

            ax1.set_xlabel('Time since Midnight (hours)')
            ax1.set_ylabel('Temperature (F)', color='r')
            ax2.set_ylabel('R-value', color='b')
            plt.savefig('webapp/static/graph1.png')


            fig2, ax1 = plt.subplots()

            ax2 = ax1.twinx()

            ax1.plot(d_avg, T_avg, 'r-')
            ax2.plot(d_avg, R_avg, 'b-')

            ax1.set_xlabel('Day of Week (Sunday = 1)')
            ax1.set_ylabel('Temperature (F)', color='r')
            ax2.set_ylabel('R-value', color='b')
            plt.savefig('webapp/static/graph2.png')

        
        #outputs current state
        print('Duration: '+str(round(t_step,3))+' (sec) | Measured Temp: '+str(round(room_temp_f,3))+" F | Predicted Temp: "+str(round(p_room_temp_f,3))+" F | HVAC Temp: "+str(round(hvac_temp_f,3))+' F | Goal Temp: +'+str(round(goal_temp_f,3))+' F | Outside Temp: '+str(round(out_temp_f,3))+' F | AC: '+str(ac)+' | Heat: '+str(heat)+' | Fan: '+str(fan))

        #outputs current temp and hvac status for use in homebridge
        f = open('operating_values/room_temp.csv','w')
        f.write(str(round(room_temp_f,3)))
        f.close()
        f = open('operating_values/hvac.csv','w')
        f.write('fan,heat,ac\n'+str(fan)+','+str(heat)+','+str(ac))
        f.close()
        
        #wait 1 second to reduce error rate
        time.sleep(1)
    except RuntimeError as error:
        time.sleep(1)
        continue
    except KeyboardInterrupt as error:
        GPIO.output(fan_pin, GPIO.LOW)
        GPIO.output(ac_pin, GPIO.LOW)
        GPIO.output(heat_pin, GPIO.LOW)
        dhtDevice.exit()
        raise error
    except Exception as error:
        dhtDevice.exit()
        raise error

#reset pins on shutdown to turn off hvac system
GPIO.output(fan_pin, GPIO.LOW)
GPIO.output(ac_pin, GPIO.LOW)
GPIO.output(heat_pin, GPIO.LOW)