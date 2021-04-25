import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

goal_temp_f = 70 #K
room_temp_f = 80 #F
hvac_temp_f = 80 #F
out_temp_f = 80 #F

goal_temp_k = (5/9 * (goal_temp_f - 32)) + 273.15 #K
room_temp_k = (5/9 * (room_temp_f - 32)) + 273.15 #K
hvac_temp_k = (5/9 * (hvac_temp_f - 32)) + 273.15 #K
out_temp_k = (5/9 * (out_temp_f - 32)) + 273.15 #K

room_capacity = 123 #kJ/K
hvac_capacity = 10 #kJ/K #sum must be 133

room_heat = room_temp_k*room_capacity #kJ
hvac_heat = hvac_temp_k*hvac_capacity #kJ

ac_power = 928.58 #kJ/hr
heat_power = 5000 #kJ/hr


t = 0  #sec
t_step = 1 #sec

R1 = 40 # K/kJ*sec
R2 = 10 # K/kJ*sec

ts = [0] #sec
room_ts = [room_temp_f] #F
hvac_ts = [hvac_temp_f] #F

heat = 0
ac = 0
fan = 1

tolerance = 0.5

while t<100:

    out_temp_f = 70-10*np.cos(2*math.pi*t/86400) #starts at sunrise
    out_temp_k = (5/9 * (out_temp_f - 32)) + 273.15 #K

    dQ_out_room = (1/R1)*(out_temp_k - room_temp_k)*t_step #kJ
    dQ_room_hvac = (1/R2)*(room_temp_k - hvac_temp_k)*t_step #kJ

    dQ_heat = (heat_power/3600)*t_step
    dQ_ac = (ac_power/3600)*t_step

    t = t + t_step #sec
    room_heat = room_heat + dQ_out_room - dQ_room_hvac #kJ
    hvac_heat = hvac_heat + dQ_room_hvac #kJ

    if room_temp_f > goal_temp_f + tolerance:
        fan = 1
        ac = 1
        heat = 0
    if room_temp_f < goal_temp_f - tolerance:
        fan = 1
        ac = 0
        heat = 1

    if heat:
        hvac_heat=hvac_heat+dQ_heat
    if ac:
        hvac_heat=hvac_heat-dQ_ac
    
    if fan:
        R2 = 5
    else:
        R2 = 10

    room_temp_k = room_heat/room_capacity #K
    hvac_temp_k = hvac_heat/hvac_capacity #K

    room_temp_f = ((room_temp_k - 273.15) * 9/5) + 32 #F
    hvac_temp_f = ((hvac_temp_k - 273.15) * 9/5) + 32 #F

    ts.append(t/3600) #hours
    room_ts.append(room_temp_f) #F
    hvac_ts.append(hvac_temp_f) #F

figure = plt.figure()
graph = figure.add_subplot(111)
graph.plot(ts,room_ts,'-',c='red')
graph.plot(ts,hvac_ts,'-',c='blue')
red_patch = mpatches.Patch(color='red', label='Room Temp')
blue_patch = mpatches.Patch(color='blue', label='hvac Temp')
plt.legend(handles=[blue_patch,red_patch])
graph.set_xlabel('Time (hours)')
graph.set_ylabel('Temperature ')
plt.show()


