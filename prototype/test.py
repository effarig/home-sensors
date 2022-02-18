#! /usr/bin/env python

import board
import digitalio
import busio
import time
import adafruit_bme280.basic as adafruit_bme280

def setup(i2c, address):
    overscan = adafruit_bme280.OVERSCAN_X16
    bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
    bme.sea_level_pressure   = 1013.25
    bme.overscan_temperature = overscan
    bme.overscan_humidity    = overscan
    bme.overscan_pressure    = overscan
    return bme

def fetch_values(attr, bmes):
    for bme in bmes:
        yield getattr(bme, attr)

def show(title, fmt, attr, bmes):
    texts = [ fmt.format(v).ljust(15) for v in fetch_values(attr, bmes) ]
    print("{} {}".format(title, " ".join(texts)))

i2c = busio.I2C(board.SCL, board.SDA)

bmes = [
    setup(i2c, 0x77),
#   setup(i2c, 0x76),
]

temps = [ #"28-00000584e10e", "28-000009128aca",
          "28-000009134cd2", # Internal
          #"28-000009140017", "28-000009a23a4c",
          #"28-000009a2fa57", "28-000009a307d0", "28-000009a331eb", "28-000009b598e9"
]


while True:
    print()
    show("Temperature    ", "{:0.1f} C"     , "temperature", bmes)
    show("Humidity       ", "{:0.1f} %"     , "humidity"   , bmes)
    show("Pressure       ", "{:0.1f} hPA"   , "pressure"   , bmes)
    show("Altitude       ", "{:0.2f} meters", "altitude"   , bmes)

    for t in temps:
      try:
        with open("/sys/bus/w1/devices/{}/w1_slave".format(t)) as f:
            lines = [ l.strip() for l in f ]
            value = None
            assert(len(lines)==2)
            assert(lines[0].endswith(" YES"))
            tt = lines[1].rfind("t=")
            if tt>=0:
                value = float(lines[1][tt+2:])/1000
            print("{} {:0.1f} C".format(t, value))
      except FileNotFoundError:
        print("{} not found.".format(t))
    time.sleep(10)
