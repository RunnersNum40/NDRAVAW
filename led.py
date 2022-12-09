import os
import json
import time
import requests
import threading

from datetime import datetime
from typing import List

import numpy as np
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
    def __init__(self, plate_pins: List[int], plate_files: List[str], cache_data: bool = True) -> None:
        # Setup all the pins
        for pin in plate_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Store object parameters
        self.plates = [PressurePlate(pin) for pin in plate_pins]
        self.plate_files = plate_files
        self.cache_data = cache_data

        self.plate_tracker = threading.Thread(target=self.plate_reader, args=(1000,))
        self.plate_tracker.start()

    def main_loop(self) -> None:
        """Main loop to run the event. Send the playlist in plate_files[# of plates] whenever a plate is changed."""
        if self.cache_data:
            # Read all the json files
            plate_data = tuple(read_json(file_name) for file_name in self.plate_files)
        # Intalize the plate pins and old_plates out of range
        plates, old_plates = self.plate_states, []
        # Run forever
        while True:
            # Check if the number of plates activaited has changed
            num_plates = sum(plates)
            if num_plates != sum(old_plates):
                print(plates)
                if self.cache_data:
                    r = send_json(plate_data[num_plates])
                else:
                    r = send_json(read_json(self.plate_files[num_plates]))
                # Wait to avoid flickering if broken
                time.sleep(1)
            # Check if the state has changed
            if plates != old_plates:
                # Save the old state
                old_plates = plates
<<<<<<< Updated upstream
                # Wait to avoid flickering if broken
                time.sleep(1)
            # Find the current state of the event
            plates = self.plate_states

    def plate_reader(self, max_poll_history: int = 1000):
        """Asynchronusly keep track of the plate history.
        
        Args:
            max_poll_history (int): Number of previous polls to consider (default: `1000`)
        """
        lock = threading.Lock()
        plates_history = np.empty((len(self.plates),))
        while True:
            with lock:
                # Read the current states
                plate_history.append(self.read_plate_states())
                # Restrict the number of polls considered
                if len(plate_history) > max_poll_history:
                    plate_history = numpy.delete(plate_history, (0), axis=0)
                # Average and cast to int
                self.plate_states = np.mean(plate_history, axis=0, dtype=np.int32)

    def read_plate_states(self):
        """Return the state of all the plates"""
        return [plate.state() for plate in self.plates]
=======
            # Find the current state
            plates = [plate.state() for plate in self.plates]
>>>>>>> Stashed changes

    def __del__(self):
        # Finish with the gpio pins
        GPIO.cleanup()