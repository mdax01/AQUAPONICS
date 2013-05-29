#!/usr/bin/env python
# DS18B20 Temperature script 
# mdax v.1

import os
import glob
import time
import json
import subprocess

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*4b0*')[0]
device_file = device_folder + '/w1_slave'

timestr = time.strftime("%Y%m%d-%H%M")

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        # Read temp, set proper decimal place for C, then convert to F. Separate /1000 and * 1.8 + 32 if you want separate C and F readings
        temp = float(temp_string) / 1000.0 * 1.8 + 32
        # Round temp to 2 decimal points
        temp = round(temp, 2)
        return temp

while True:
        # Uncomment print command to print output
        #print(read_temp())

        # Send the data to Cosm
        temp = read_temp()
        data = json.dumps({"version":"1.0.0", "datastreams":[{"id":"Water_Temperature","current_value":temp}]})
        with open("temp.tmp", "w") as f:
            f.write(data)

        subprocess.call(['curl --request PUT --data-binary @temp.tmp --header "X-ApiKey: HetxMuRJgurobKjxnfNkyIyWmuCVSVxmfeA5yY1gWZvM2GeS" https://api.xively.com/v2/feeds/412741963'], shell=True)

        with open("WaterTempOutput", "a") as f:
            f.write("%s, %s\n" % (timestr, temp))

        os.remove("temp.tmp")

        break
