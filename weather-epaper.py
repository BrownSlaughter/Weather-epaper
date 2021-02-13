#!/usr/bin/python
# -*- coding:utf-8 -*-
##Weather e-paper Test v1
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import time
# Lets import some required libraries that will be used to gather and display the information.
import requests, json

import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from pushbullet import Pushbullet
pb = Pushbullet("****token*****")

logging.basicConfig(level=logging.DEBUG)

def deg_to_dir(d):

    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = int(d / (360 / len(dirs)))
    return dirs[ix % len(dirs)]

##make weather dictionary
weathericons = {
  "Thunderstorm": "I",
  "Clouds": "A",
  "Mist": "C",
  "Snow": "H",
  "Clear": "J",
  "Drizzle": "g",
  "Fog": "C",
  "shower rain": "G",
  "Mist": "C",
  "Smoke": "C",
  "Haze": "C",
  "Sand": "C",
  "Dust": "C",
  "Ash": "C",
  "Squall": "C",
  "Tornado": "L",
  "Rain": "G"
}

# Get and load the weather data
logging.info("Getting Weather")

response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=**********,uk&units=metric&appid=****************")
x= response.json()
y = x["main"]
z = x["weather"]
wind = x["wind"]
sun =  x["sys"]
location = x["name"]
current_temperature = y["temp"]
current_feels = y["feels_like"]
current_main = z[0]["main"]
current_description = z[0]["description"]
current_icon = weathericons[current_main]
sunrise_time = sun["sunrise"]
sunset_time = sun["sunset"]
wind_speed = wind["speed"]
wind_deg = wind["deg"]
wind_dir = deg_to_dir(wind_deg)

#pushbullet
if current_main == "Snow":
   Print ("snow")
   dev = pb.get_device('Xiaomi Mi A2')
   push = dev.push_note("Hey check the weather!", "Its apparently snowing!")

#Timey whimey Stuff
epoch_time = time.time()
time_now = time.strftime('%H:%M', time.localtime(epoch_time))
date_now = time.strftime('%a-%d-%b', time.localtime(epoch_time))
sunrise = time.strftime('%H:%M', time.localtime(sunrise_time))
sunset = time.strftime('%H:%M', time.localtime(sunset_time))

try:
    epd = epd2in13_V2.EPD()
    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

# Drawing on the image
    font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    wfont48 = ImageFont.truetype(os.path.join(picdir, 'font2.ttf'), 48)
    wfont35 = ImageFont.truetype(os.path.join(picdir, 'font2.ttf'), 35)

    logging.info("1.Drawing on the image...")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 263, 175), outline = 0)
    draw.text((3, 0), str(current_icon), font = wfont48, fill = 0)
    draw.text((50, 4), str(location), font = font24, fill = 0)
    draw.text((200, 16), str(time_now), font = font15, fill = 0)
    draw.text((180, 1), str(date_now), font = font15, fill = 0)
    draw.line((0, 35, 263, 35), fill = 0)
    draw.text((3, 35), "Weather = " + str(current_description), font = font15, fill = 0)
    draw.text((3, 52), "Temp " + str(current_temperature) + " C, Feels like " + str(current_feels) + " C", font = font15, fill = 0)
    draw.text((3, 67), "Wind Speed = " + str(wind_speed) + "mph, " + str(wind_dir) , font = font15, fill = 0)

    draw.text((3, 100), "J", font = wfont35, fill = 0)
    draw.text((27, 103), str(sunrise), font = font15, fill = 0)
    draw.text((77, 100), "K", font = wfont35, fill = 0)
    draw.text((99, 103), str(sunset), font = font15, fill = 0)

    epd.display(epd.getbuffer(image))

    logging.info("Exiting")
    epd.sleep()
    #time.sleep(3)
    epd.Dev_exit()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V2.epdconfig.module_exit()
    exit()
