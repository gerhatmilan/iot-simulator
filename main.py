from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

from smarthome.automation_system import *
from smarthome.devices import *

import threading
import time

'''
Tkinter GUI app for Smart Home
'''
class SmartHomeGUI(Tk):
    WINDOW_WIDTH_PERCENTAGE = 0.8

    def __init__(self):
        super().__init__()
        self.system = AutomationSystem()
        self.title("Smart Home")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.column_width = self.screen_width * self.WINDOW_WIDTH_PERCENTAGE * 0.5
        self.geometry(f"{int(self.screen_width * self.WINDOW_WIDTH_PERCENTAGE)}x{int(self.screen_height * 0.8)}")
        self.style = Style()
        self.style.configure('.', font=("Arial", 17))
        self.resizable(False, False)
        self.button_style = Style()
        self.button_style.configure("Red.TButton", background="red")
        self.button_style.configure("Green.TButton", background="green")
        

        # Title
        self.title_label = Label(self, text="Smart Home", font=('Arial', 30))
        self.title_label.pack(pady=10)
        
        # Main Frame
        self.frame = Frame(self)
        self.frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Devices column
        self.first_column_frame = Frame(self.frame)
        self.first_column_frame.pack(side=LEFT, fill=Y)

        self.rules_label = Label(self.first_column_frame, text='Automation rules', font=('Arial', 25))
        self.rules_label.pack(pady=10)

        for rule in self.system.automations:
            Label(self.first_column_frame, text=rule.description, font=('Arial', 15)).pack(pady=10)
        
        self.devices_label = Label(self.first_column_frame, text='My devices', font=('Arial', 25))
        self.devices_label.pack(pady=10)

        self.add_new_button = Button(self.first_column_frame, text="Add new device...", command=self.create_add_window)
        self.add_new_button.pack(pady=10)
        self.start_simulation_button = Button(self.first_column_frame, text="Start simulation", command=self.start_simulation)
        self.start_simulation_button.pack(pady=10)
        self.stop_simulation_button = Button(self.first_column_frame, text="Stop simulation", command=self.stop_simulation, state=DISABLED)
        self.stop_simulation_button.pack(pady=10)

        self.canvas1 = Canvas(self.first_column_frame, bg="white", width=self.column_width)
        self.scrollbar1 = Scrollbar(self.first_column_frame, orient="vertical", command=self.canvas1.yview)
        self.canvas1.config(yscrollcommand=self.scrollbar1.set)
        
        self.canvas1.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar1.pack(side=RIGHT, fill=Y)

        y_coordinate = 0
        block_height = 150
        self.device_blocks = {}
        for i in range(self.system.MAX_DEVICES):
            block = Frame(self.canvas1, width=self.column_width, height=block_height)
            block.pack(pady=10, padx=10)

            button = Button(block, style='Red.TButton')
            button.grid_forget()
            self.device_blocks[i] = {
                'block': block,
                'deviceNameLabel': Label(block),
                'toggleButton': button,
                'labelOne': Label(block),
                'scale': Scale(block),

            }
            
            self.canvas1.create_window((0, y_coordinate), window=block, anchor="nw")
            y_coordinate += block_height
        
        # Logs column   
        self.second_column_frame = Frame(self.frame)
        self.second_column_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        self.logs_label = Label(self.second_column_frame, text='Logs', font=('Arial', 25))
        self.logs_label.pack(pady=10) 

        self.canvas2 = Canvas(self.second_column_frame, bg="white", width=self.column_width) 
        self.canvas2.pack(side=LEFT, fill=BOTH, expand=True)

        y_coordinate = 0
        block_height = 25
        self.log_labels = []
        for i in range(AutomationSystem.MAX_LOGS):
            block = Frame(self.canvas2, width=self.column_width, height=block_height)
            label = Label(block, font=('Arial', 13))
            self.log_labels.append(label)
            label.pack(expand=True)
            block.pack(pady=5, padx=5)
            self.canvas2.create_window((0, y_coordinate), window=block, anchor="nw")
            y_coordinate += block_height

    '''
        Responsible for creating a new window when adding a new device
    '''
    def create_add_window(self):
        self.add_device_window = Toplevel(self)
        self.add_device_window.title("Add device")
        self.add_device_window.geometry("500x500")
        
        frame = Frame(self.add_device_window)
        frame.pack(side=LEFT, fill=BOTH, expand=True)

    
        self.selected_option = StringVar()

        label1 = Label(frame, text=f"Device type")
        label1.pack(padx=10, pady=10)
        
        radio_button1 = Radiobutton(frame, text="Smart Light", variable=self.selected_option, value='Smart Light')
        radio_button2 = Radiobutton(frame, text="Thermostate", variable=self.selected_option, value='Thermostate')
        radio_button3 = Radiobutton(frame, text="Security Camera", variable=self.selected_option, value='Security Camera')
        radio_button1.pack(padx=10, pady=10, fill='x')
        radio_button2.pack(padx=10, pady=10, fill='x')
        radio_button3.pack(padx=10, pady=10, fill='x')


        label2 = Label(frame, text="Set a name for the device:")
        label2.pack(padx=10, pady=20)

        self.input_entry = Entry(frame, font=('Arial', 20))
        self.input_entry.pack(padx=70, pady=10, fill='x')
        
        submit_button = Button(frame, text="Add", command=self.add_device_command)
        submit_button.pack(pady=10)

        
    '''
        The command which is responsible for adding a new device object to the system object.
    '''
    def add_device_command(self):
        device_type = self.selected_option.get()
        name = self.input_entry.get()

        try:
            if device_type:
                match device_type:
                    case 'Smart Light':
                        self.system.add_device(SmartLight(self.system.device_id_count, name))
                    case 'Thermostate':
                        self.system.add_device(Thermostat(self.system.device_id_count, name))
                    case 'Security Camera':
                        self.system.add_device(SecurityCamera(self.system.device_id_count, name))
                self.system.increase_id_count()
                self.update_device_view()
                self.add_device_window.destroy()     
        except AutomationSystem.DeviceLimitReached as ex:
            messagebox.showinfo("Info", ex)    


    '''
        Command for changing a device state
    '''
    def toggle_button_command(self, device):
        device.turn_off(self.system) if device.get_status() == Status.ON else device.turn_on(self.system)
        self.update_device_view()

    '''
        Command for updating a device's brightness according to user input
    '''
    def on_brightness_change(self, scale, device):
        if not isinstance(device, SmartLight):
            raise ValueError('This method can only work on Smart Lights')

        if (device.get_status()==Status.ON):
            device.set_brightness(self.system, int(scale.get()))
            self.update_device_view()
    
    '''
        Command for updating a device's temperature according to user input
    '''
    def on_temperature_change(self, scale, device):
        if not isinstance(device, Thermostat):
            raise ValueError('This method can only work on Smart Lights')
        
        if (device.get_status()==Status.ON):
            device.set_temperature(self.system, int(scale.get()))
            self.update_device_view()

    '''
    Updating the widgets in the left-side canvas
    '''
    def update_device_view(self):
        for idx, device in enumerate(self.system.get_devices()):
            self.device_blocks[idx]['deviceNameLabel'].config(text=device.get_name())
            self.device_blocks[idx]['deviceNameLabel'].grid(row=idx, column=0, sticky="w", padx=10, pady=10)
            
            self.device_blocks[idx]['toggleButton'].config(text=f"{'Toggle ON' if device.get_status() == Status.OFF else 'Toggle OFF'}")
            self.device_blocks[idx]['toggleButton'].config(style=f"{'Red.TButton' if device.get_status() == Status.OFF else 'Green.TButton'}")
            self.device_blocks[idx]['toggleButton'].bind("<Button-1>", lambda event, param=device: self.toggle_button_command(param))
            self.device_blocks[idx]['toggleButton'].grid(row=idx, column=1, sticky="w", padx=10, pady=10)

            if isinstance(device, SmartLight):
                self.device_blocks[idx]['labelOne'].config(text=f'Current brightness: {"0" if device.get_status()==Status.OFF else device.get_brightness()}%')
                self.device_blocks[idx]['labelOne'].grid(row=idx + 1, column=0, columnspan=2, sticky='w', padx=50, pady=5)

                self.device_blocks[idx]['scale'].config(from_=SmartLight.MIN_BRIGHTNESS, to=SmartLight.MAX_BRIGHTNESS, orient="horizontal", length=300)
                self.device_blocks[idx]['scale'].set(device.get_brightness())
                self.device_blocks[idx]['scale'].grid(row=idx + 2, column = 0, columnspan = 2, sticky='w', padx=50, pady=5)
                self.device_blocks[idx]['scale'].bind("<ButtonRelease-1>", lambda event, param1=self.device_blocks[idx]['scale'], param2=device: self.on_brightness_change(param1, param2))
            elif isinstance(device, Thermostat):
                self.device_blocks[idx]['labelOne'].config(text=f'Current temperature: {"Unknown" if device.get_status()==Status.OFF else str(device.get_temperature()) + "°C"}')
                self.device_blocks[idx]['labelOne'].grid(row=idx + 1, column=0, columnspan=2, sticky='w', padx=50, pady=5)

                self.device_blocks[idx]['scale'].config(from_=Thermostat.MIN_TEMP, to=Thermostat.MAX_TEMP, orient="horizontal", length=300)
                self.device_blocks[idx]['scale'].set(device.get_temperature())
                self.device_blocks[idx]['scale'].grid(row=idx + 2, column = 0, columnspan = 2, sticky='w', padx=50, pady=5)
                self.device_blocks[idx]['scale'].bind("<ButtonRelease-1>", lambda event, param1=self.device_blocks[idx]['scale'], param2=device: self.on_temperature_change(param1, param2))
            elif isinstance(device, SecurityCamera):
                self.device_blocks[idx]['labelOne'].config(text=f'Current security state: {"Unknown" if device.get_status() == Status.OFF else device.get_security_status().name}')
                self.device_blocks[idx]['labelOne'].grid(row=idx + 1, column=0, columnspan=2, sticky='w', padx=50, pady=5)

        self.update_logs_view()
        self.canvas1.update_idletasks()
        self.canvas1.config(scrollregion=self.canvas1.bbox("all"))

    '''
    Updating the widgets in the right-side canvas
    '''
    def update_logs_view(self):
        for idx, log in enumerate(self.system.logs):
            self.log_labels[idx].config(text=log)

    '''
    Stopping the simulation thread
    '''
    def stop_simulation(self):
        self.system.stop_simulation()
        self.stop_simulation_button.config(state=DISABLED)
        self.start_simulation_button.config(state=ACTIVE)

    '''
    Starting the simulation thread
    '''
    def start_simulation(self):
        if not self.system.can_run_simulation():
            return
        
        # Starting a thread to refresh the view in certain interval
        self.view_thread = threading.Thread(target=lambda: self.refresh_view())
        self.view_thread.daemon = True
        

        self.start_simulation_button.config(state=DISABLED)
        self.stop_simulation_button.config(state=ACTIVE)
        self.simulation_thread = threading.Thread(target=lambda: self.system.start_simulation())
        self.simulation_thread.daemon = True

        self.simulation_thread.start()
        self.view_thread.start()

    '''
    Starting a separate thread for updating the widgets in certain interval while the simulation is running
    '''
    def refresh_view(self):
        while self.system.sim_is_running:
            self.update_device_view()
            time.sleep(0.01)
        

'''
Main program
'''
if __name__ == "__main__":
    app = SmartHomeGUI()
    try:
        app.mainloop()
    except:
        exit()

