import os
import json
import time
import requests

from datetime import datetime
from typing import List

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

script_path = os.path.dirname(__file__)+"/"
WLED_URL = "http://4.3.2.1/json"

def read_json(file_name: str) -> dict:
    """Return a dict copy of the contents of a json file.

    Args:
        file_name: String file name to read
    Returns:
        Dictionary of json data read
    """
    with open(script_path+file_name, "r") as file:
        data = json.load(file)
    return data

def send_json(data: dict, url: str = WLED_URL) -> object:
    """Send a json dict to a url with a POST request.

    Args:
        data: Dictionary of json data to send
        url: URL to send the data to
    Returns:
        A requests response object
    """
    r = requests.request(method="POST", url=url, json=data)
    return r


class PressurePlate:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def state(self):
        return GPIO.input(self.pin)


class Event:
    """An event for the National Day of Rememberance and Action on Violence Against Women"""
    def __init__(self, plate_pins: List[int], plate_files: List[str], cache_data: bool = True, logging_file_name: str = None) -> None:
        # Setup all the pins
        for pin in plate_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Add the headers to the logging file
        if logging_file_name is not None:
            with open(script_path+logging_file_name, "w") as logging_file:
                logging_file.write(f"datetime,{','.join(map(str, plate_pins))}\n")
        # Store object parameters
        self.plates = [PressurePlate(pin) for pin in plate_pins]
        self.plate_files = plate_files
        self.cache_data = cache_data
        self.logging_file_name = logging_file_name

    def main_loop(self) -> None:
        """Main loop to run the event. Send the playlist in plate_files[# of plates] whenever a plate is changed."""
        if self.cache_data:
            # Read all the json files
            plate_data = tuple(read_json(file_name) for file_name in self.plate_files)
        # Intalize the plate pins and old_plates out of range
        plates, old_plates = [plate.state() for plate in self.plates], []
        # Run forever
        while True:
            # Check if the number of plates activaited has changed
            num_plates = sum(plates)
            if num_plates != sum(old_plates):
                if self.cache_data:
                    r = send_json(plate_data[num_plates])
                else:
                    r = send_json(read_json(self.plate_files[num_plates]))
            # Check if the state has changed
            if plates != old_plates:
                # Log the time and state of all pins
                if self.logging_file_name is not None:
                    with open(script_path+self.logging_file_name, "a") as logging_file:
                        logging_file.write(f"{datetime.now()},{','.join(map(str, plates))}\n")
                # Save the old state
                old_plates = plates
                # Wait to avoid flickering if broken
                time.sleep(1)
            # Find the current state
            plates = [plate.state() for plate in self.plates]

    def __del__(self):
        # Finish with the gpio pins
        GPIO.cleanup()