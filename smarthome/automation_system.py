from abc import ABC, abstractmethod

from datetime import time
from datetime import *
import time
import threading

from smarthome.devices import *


'''
    Abstract class representing an automation rule
'''
class AutomationRule:
    def __init__(self, description):
        self.description = description

    @abstractmethod
    def __run(self):
        pass

'''
    Automation rule: turns off every light in the system when a camera alerts
'''
class TurnOffCamerasOnAlert(AutomationRule):
    def __init__(self):
        super().__init__('Turn off every light when one of the Security Cameras\' status changes to \"ALERT\"')
    
    '''
        Turns off every smart light in the system
    '''
    def __turn_off_lights(self, system):
        for device in system.get_devices():
            if isinstance(device, SmartLight):
                device.turn_off(system)

    '''
        While the simulation is running, it keeps checking if any of the cameras is on ALERT.
        If so, then it turns off the lights in the system
    '''
    def __run(self, system):
        while system.sim_is_running:
            for device in system.get_devices():
                if isinstance(device, SecurityCamera) and device.get_security_status() == SecurityStatus.ALERT:
                    self.__turn_off_lights(system)
                    break
            time.sleep(0.5)
    
    '''
        Starts a thread which runs the automation
    '''
    def start(self, system):
        thread = threading.Thread(target=lambda: self.__run(system))
        thread.daemon = True
        thread.start()


'''
    Automation System class for managing smart devices
'''
class AutomationSystem:
    '''
        Exception which can be raised when it is attempted to add a device after reaching the device limit
    '''
    class DeviceLimitReached(Exception):
        def __init__(self, msg):
            super().__init__(msg)

    MAX_DEVICES = 20
    MAX_LOGS = 20
    
    def __init__(self):
        self.__devices = []
        self.device_id_count = 1
        self.logs = []
        self.automations = [TurnOffCamerasOnAlert()]
        self.__sim_should_run = False
        self.sim_is_running = False      
    '''
        Returns the current time in YYYY.MM.DD HH:MM:SS format
    '''
    def __get_current_time(self):
        current_time = datetime.now()
        return current_time.strftime("%Y.%m.%d %H:%M:%S")
    
    '''
        Adds a new message to the stored message list
    '''
    def add_log(self, msg):
        if len(self.logs) == self.MAX_LOGS:
            self.logs.pop()
        self.logs.insert(0, f'{self.__get_current_time()} - {msg}')

    '''
        Returns the devices of the system
    '''
    def get_devices(self):
        return self.__devices
    
    '''
        Sets a new, unique id for the next device
    '''
    def increase_id_count(self):
        self.device_id_count += 1
    
    '''
        Adds a new device to the system
    '''
    def add_device(self, device):
        if len(self.__devices) < self.MAX_DEVICES:
            self.__devices.append(device)
            self.add_log(f'Device added: {device.get_name()}')
        else:
            raise self.DeviceLimitReached('Can not add more devices: maximum reached')      

    '''
        Removes a device from the system
    '''
    def remove_device(self, device):
        self.__devices.remove(device)
        self.add_log(f'Device removed: {device.get_name()}')

    '''
        Checks if it is possible to run the simulation at the current state
    '''
    def can_run_simulation(self):
        for device in self.__devices:
            if device.get_status() == Status.ON:
                return True
        return False

    '''
        Starts the simulation
    '''
    def start_simulation(self):
        if not self.can_run_simulation():
            return

        self.add_log('Simulation running...')
        self.__sim_should_run = True
        self.sim_is_running = True

        self.__start_automations()

        while self.__sim_should_run:
            for device in self.__devices:
                if device.run_simulation(self):
                    time.sleep(2)
            time.sleep(5)

        self.add_log('Simulation stopped')
        self.sim_is_running = False

    '''
        Stops the simulation
    '''
    def stop_simulation(self):
        self.add_log('Stopping simulation...')
        self.__sim_should_run = False

    def __start_automations(self):
        for automation in self.automations:
            automation.start(self)
    