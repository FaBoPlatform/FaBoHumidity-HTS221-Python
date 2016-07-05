# coding: utf-8
## @package FaBoHumidity_HTS221
#  This is a library for the FaBo Humidity I2C Brick.
#
#  http://fabo.io/208.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

import FaBoHumidity_HTS221
import time

hts221 = FaBoHumidity_HTS221.HTS221()

while True:
    humi = hts221.readHumi()
    temp = hts221.readTemp()
    print "Humidity = ", humi
    print "Temp     = ", temp
    print
    time.sleep(1)
