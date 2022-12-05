import os
import time
import logging

from led import Event

# time.sleep(10)

try:
    plate_pins = (23, 24)
    plate_files = ("states/0p.json", "states/1p.json", "states/2p.json")
    event = Event(plate_pins, plate_files, cache_data=True, logging_file_name="logs/log.csv")
    event.main_loop()
except Exception as e:
    print(e)
    with open("/home/pi/error_log.txt", "w") as file:
        file.write(str(e))