from abc import ABC, abstractmethod
from enum import Enum
import time
import random

'''
    Enumeration representing a power state
'''
class Status(Enum):
    OFF = 1
    ON = 2

'''
    Enumeration representing a security camera state
'''
class SecurityStatus(Enum):
    SAFE = 1
    ALERT = 2

'''
    Abstract device class for smart devices
'''
class Device(ABC):
    '''
        Exception which can be raised when an illegal argument was given
    '''
    class IllegalParameter(Exception):
        def __init__(self, msg):
            super().__init__(msg) 

    def __init__(self, id, name=None):
        if id < 0:
            raise self.IllegalParameter('ID must be non-negative.')
        self.__status = Status.OFF
        self.__id = id
        if name:
            self.__name = name
        else:
            self.__name = f'Device #{id}'

    '''
        Returns the id of the device
    '''
    def get_id(self):
        return self.__id
    
    '''
        Returns the power status of the device
    '''
    def get_status(self):
        return self.__status
    
    '''
        Returns the name of the device
    '''
    def get_name(self):
        return self.__name
    
    '''
        Sets a new name for the device
    '''
    def set_name(self, name):
        self.__name = name
    
    '''
        Turns on the device
    '''
    def turn_on(self, system):
        if self.__status == Status.OFF:
            self.__status = Status.ON
            system.add_log(f'{self.get_name()} turned ON')

    '''
        Turns off the device
    '''
    def turn_off(self, system):
        if self.__status == Status.ON:
            self.__status = Status.OFF
            system.add_log(f'{self.get_name()} turned OFF')

    '''
        Abstract method for running the simulation of a device
    '''
    @abstractmethod
    def run_simulation(self, system):
        pass

'''
    Class representing a smart light
'''
class SmartLight(Device):
    MIN_BRIGHTNESS = 1
    MAX_BRIGHTNESS = 100 
    DEFAULT_BRIGHTNESS = 50

    def __init__(self, id, name=None, brightness=DEFAULT_BRIGHTNESS):
        if brightness < 1 or brightness > 100:
            raise super().IllegalParameter('Brightness must be between 1 and 100.')
        super().__init__(id, name)
        self.__brightness = brightness

    '''
        Returns the current brightness level of the light
    '''
    def get_brightness(self):
        return self.__brightness
    
    '''
        Sets the brightness to the given level
        Sends a message to the system
    '''
    def set_brightness(self, system, new_brightness):
         if new_brightness < self.MIN_BRIGHTNESS or new_brightness > self.MAX_BRIGHTNESS:
            raise super().IllegalParameter(f'Brightness must be between {self.MIN_BRIGHTNESS} and {self.MAX_BRIGHTNESS}')
         self.__brightness = new_brightness
         system.add_log(f'{self.get_name()}: Brigthness set to {new_brightness}%')

    '''
        Sets the brightness level gradually. This method is part of the simulation
        Sends a message to the system
    '''
    def __gradual_dimming(self, system, new_brightness):
        system.add_log(f'{self.get_name()}: Changing brightness to {new_brightness}%...')
        while self.get_status() == Status.ON and self.__brightness != new_brightness:
            if new_brightness > self.__brightness:
                self.__brightness += 1
                time.sleep(0.05)
            elif new_brightness < self.__brightness:
                self.__brightness -= 1
                time.sleep(0.05)
        system.add_log(f'{self.get_name()}: Brightness set to {new_brightness}%')


    '''
        Runs a randomised simulation for the light, if possible
        Returns true if the run was successful, false otherwise
    '''
    def run_simulation(self, system):
        if self.get_status() == Status.OFF:
            return False
        new_brightness = random.randint(1, 100)
        self.__gradual_dimming(system, new_brightness)
        return True

'''
    Class representing a smart thermostat
'''
class Thermostat(Device):
    MIN_TEMP = -10
    MAX_TEMP = 30
    DEFAULT_TEMP = 15

    def __init__(self, id, name=None, temperature=DEFAULT_TEMP):
        if temperature < self.MIN_TEMP or temperature > self.MAX_TEMP:
            raise super().IllegalParameter(f'Temperature must be between {self.MIN_TEMP} and {self.MAX_TEMP}.')
        super().__init__(id, name)
        self.__temperature = temperature

    '''
        Returns the current temperature
    '''
    def get_temperature(self):
        return self.__temperature
    
    '''
        Sets the current temperature to the given value
        Sends a message to the system
    '''
    def set_temperature(self, system, temperature):
        if temperature < self.MIN_TEMP or temperature > self.MAX_TEMP:
            raise super().IllegalParameter('Temperature must be between {self.__MIN_TEMP} and {self.__MAX_TEMP}.')
        self.__temperature = temperature    
        system.add_log(f'{self.get_name()}: Temperature set to {self.__temperature}°C') 

    '''
        Returns the current desired temperature
    '''
    def get_desired_temp(self):
        return self.__desired_temp
    
    '''
        Sets the desired temperature to the given value
    '''
    def set_desired_temp(self, desired_temp):
        self.__desired_temp = desired_temp

    '''
        Simulates a gradual heating or cooling
        Sends messages to the system
        This method is part of the simulation
    '''
    def __start(self, system, desired_temp):
        system.add_log(f'{self.get_name()}: Desired temperature set to {desired_temp}°C')
        while self.get_status() == Status.ON and self.__temperature != desired_temp:
            if desired_temp > self.__temperature:
                self.__temperature += 1
                time.sleep(1)
            elif desired_temp < self.__temperature:
                self.__temperature -= 1
                time.sleep(0.5)
        system.add_log(f'{self.get_name()}: Desired temperature reached. Turning off...')
        self.turn_off(system)

    '''
        Runs a randomised simulation of the thermostat, if possible
        Returns true if the run was successful, false otherwise
    '''
    def run_simulation(self, system):
        if self.get_status() == Status.OFF:
            return False
        desired_temp = random.randint(-10, 30)
        self.__start(system, desired_temp)
        return True

'''
    Class representing a smart security camera
'''
class SecurityCamera(Device):
    def __init__(self, id, name=None):
        super().__init__(id, name)
        self.__security_status = SecurityStatus.SAFE

    '''
        Returns the current security status
    '''
    def get_security_status(self):
        return self.__security_status
    
    '''
        Sets the current security status to the given status
        Sends a message to the system
        Part of the simulation
    '''
    def __set_security_status(self, system, security_status):
        self.__security_status = security_status
        system.add_log(f'{self.get_name()}: Security status changed: {self.__security_status.name}')

    '''
        Runs a randomised simulation of the device
        Alerts the system
        Returns true if the run was successful, false otherwise
    '''
    def run_simulation(self, system):
        if self.get_status() == Status.OFF:
            return False
        sim_length = random.randint(1, 10)

        self.__set_security_status(system, SecurityStatus.ALERT)

        time.sleep(sim_length)
        self.__set_security_status(system, SecurityStatus.SAFE)
        return True