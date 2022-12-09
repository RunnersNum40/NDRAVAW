import os
import time
import logging

from led import Event

# time.sleep(10)

while True:
    try:
        plate_pins = (25, 24)
        plate_files = ("states/0p.json", "states/1p.json", "states/2p.json")
        event = Event(plate_pins, plate_files, cache_data=True)
        event.main_loop()
    except Exception as e:
        print(e)
        time.sleep(5)