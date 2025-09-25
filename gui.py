#  https://www.1001fonts.com/search.html?search=lcd
#  https://kidspattern.com/color/

#  Author: JHT (Joe's Hobby Tech)  
#  Date:25/09/2025    
#  https://www.youtube.com/@joeshobbytech    
#  https://github.com/JdeV987?tab=repositories

#  Credits: 95% DeepSeek AI  ;)
#  I don't have a clue how to program anything. Just asked the right questions to AI, and ended up with this. ;)


from tkinter import *
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
import time
from dmm import OWONXDM2041

class OWONGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OWON XDM2041 Multimeter V1")
        self.root.geometry("590x230")  # Increased height for 4th row
        self.root.configure(bg='black')
        
        # Multimeter instance
        self.dmm = OWONXDM2041()
        self.update_id = None
        self.current_function = "DC Voltage"
        
        self.setup_gui()
    
    def setup_gui(self):
        # Main frame with grid layout (4x3)
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)
        
        # Configure grid weights for 4 rows with equal spacing
        for i in range(0):
            main_frame.grid_rowconfigure(i, weight=1, uniform="row")
            main_frame.grid_columnconfigure(i, weight=1)
        
        
        # Row 2: Measurement Display (centered across all columns)
        display_frame = tk.Frame(main_frame, bg='black')
        display_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=1, pady=5)
        display_frame.config(height=50)  # Fixed height in pixels
        
        # Container for value and unit (centered within display frame)
        reading_frame = tk.Frame(display_frame, bg='black')
        reading_frame.pack(expand=True, fill='both')
        
        # Value and unit in the same line, centered
        self.value_label = tk.Label(reading_frame,
                                  text="------",
                                  bg='black',
                                  fg='#A3D649',             #A3D649 GREEN,    #FFC300   GOLD
                                  font=('Poltab', 82),
                                  anchor='e')
        self.value_label.pack(side=tk.LEFT, expand=True, fill='both')
        
        self.unit_label = tk.Label(reading_frame,
                                 text="",
                                 bg='black',
                                 fg='#FFC300',
                                 font=('Helvetica', 34),
                                 anchor='sw')
        self.unit_label.pack(side=tk.LEFT, expand=True, fill='both')
        
        # Row 3: Function Buttons (centered)
        function_frame = tk.Frame(main_frame, bg='black')
        function_frame.grid(row=2, column=0, columnspan=3, sticky='nsw', pady=5)
        function_frame.config(height=50)  # Fixed height in pixels

        
        
        # Center the function buttons within their frame
        button_frame = tk.Frame(function_frame, bg='black')
        button_frame.pack(side=tk.LEFT, padx=22)

        button_container = tk.Frame(button_frame, bg='black')
        button_container.pack(expand=True)
                


        self.dc_voltage_btn = tk.Button(button_container,
                                      text="DC Voltage",
                                      command=self.set_dc_voltage,
                                      bg='grey',
                                      fg='black',
                                      font=('Arial', 10),
                                      state='disabled',
                                      width=8)
        self.dc_voltage_btn.pack(side=tk.LEFT, padx=10)
        
        self.resistance_btn = tk.Button(button_container,
                                      text="Resistance",
                                      command=self.set_resistance,
                                      bg='grey',
                                      fg='black',
                                      font=('Arial', 10),
                                      state='disabled',
                                      width=8)
        self.resistance_btn.pack(side=tk.LEFT, padx=10)
        
        self.diode_btn = tk.Button(button_container,
                                 text="Diode",
                                 command=self.set_diode,
                                 bg='grey',
                                 fg='black',
                                 font=('Arial', 10),
                                 state='disabled',
                                 width=8)
        self.diode_btn.pack(side=tk.LEFT, padx=10)

        self.cont_btn = tk.Button(button_container,
                                 text="Cont",
                                 command=self.set_cont,
                                 bg='grey',
                                 fg='black',
                                 font=('Arial', 10),
                                 state='disabled',
                                 width=8)
        self.cont_btn.pack(side=tk.LEFT, padx=10)

        self.cap_btn = tk.Button(button_container,
                                 text="Cap",
                                 command=self.set_cap,
                                 bg='grey',
                                 fg='black',
                                 font=('Arial', 10),
                                 state='disabled',
                                 width=8)
        self.cap_btn.pack(side=tk.LEFT, padx=10)


        
        # Row 4: Configuration Controls (centered)
        config_frame = tk.Frame(main_frame, bg='black')
        config_frame.grid(row=3, column=0, columnspan=3, sticky='nsw', pady=5)
        config_frame.config(height=50)    # Fixed height in pixels
        
        
        # Center the configuration controls within their frame
        config_container = tk.Frame(config_frame, bg='black')
        config_container.pack(expand=True)
        
        # Control 1: COM Port Selection
        port_frame = tk.Frame(config_container, bg='black')
        port_frame.pack(side=tk.LEFT, padx=22)
        
   #     tk.Label(port_frame, text="Port:", bg='black', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)

        self.connect_btn = tk.Button(port_frame,
                                   text="Connect",
                                   command=self.toggle_connection,
                                   bg='#e74c3c',
                                   fg='white',
                                   font=('Arial', 9, 'bold'),
                                   width=5)
        self.connect_btn.pack(side=tk.LEFT, padx=2)

        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, 
                                      textvariable=self.port_var,
                                      values=self.dmm.get_available_ports(),
                                      width=8,
                                      font=('Arial', 9))
        self.port_combo.pack(side=tk.LEFT, padx=2)
        if self.dmm.get_available_ports():
            self.port_combo.set(self.dmm.get_available_ports()[0])
        

        
        # Control 2: Rate Selection
        rate_frame = tk.Frame(config_container, bg='black')
        rate_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(rate_frame, text="Rate:", bg='black', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.rate_var = tk.StringVar(value="Medium")
        self.rate_combo = ttk.Combobox(rate_frame,
                                      textvariable=self.rate_var,
                                      values=["Slow", "Medium", "Fast"],
                                      width=8,
                                      state="readonly",
                                      font=('Arial', 9))
        self.rate_combo.pack(side=tk.LEFT, padx=2)
        self.rate_combo.bind('<<ComboboxSelected>>', self.set_rate)
        
        # Control 3: Resistance Mode (2W/4W)
        rm_frame = tk.Frame(config_container, bg='black')
        rm_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(rm_frame, text="Rmode:", bg='black', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.rmode_var = tk.StringVar(value="2W")
        self.rmode_combo = ttk.Combobox(rm_frame,
                                       textvariable=self.rmode_var,
                                       values=["2W", "4W"],
                                       width=5,
                                       state="readonly",
                                       font=('Arial', 9))
        self.rmode_combo.pack(side=tk.LEFT, padx=2)
        self.rmode_combo.bind('<<ComboboxSelected>>', self.set_rmode)
        
        # Control 4: Beep On/Off
        beep_frame = tk.Frame(config_container, bg='black')
        beep_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(beep_frame, text="Beep:", bg='black', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.beep_var = tk.StringVar(value="OFF")
        self.beep_combo = ttk.Combobox(beep_frame,
                                      textvariable=self.beep_var,
                                      values=["OFF", "ON"],
                                      width=5,
                                      state="readonly",
                                      font=('Arial', 9))
        self.beep_combo.pack(side=tk.LEFT, padx=2)
        self.beep_combo.bind('<<ComboboxSelected>>', self.set_beep)
    
    def toggle_connection(self):
        if not self.dmm.is_connected:
            self.connect_dmm()
        else:
            self.disconnect_dmm()
    
    def connect_dmm(self):
        port = self.port_var.get()
        if not port:
            self.show_error("Please select a port")
            return
        
        try:
            if self.dmm.open_serial_port(port):
                # Test connection
                idn = self.dmm.get_idn()
                print(f"Connected: {idn}")
                
                self.connect_btn.config(text="Discon.", bg='#3AB440')
                self.port_combo.config(state='disabled')
                
                # Enable function buttons and config controls
                self.dc_voltage_btn.config(state='normal')
                self.resistance_btn.config(state='normal')
                self.diode_btn.config(state='normal')
                self.cont_btn.config(state='normal')
                self.cap_btn.config(state='normal')
                self.rate_combo.config(state='readonly')
                self.rmode_combo.config(state='readonly')
                self.beep_combo.config(state='readonly')
                
                # Set default function and settings
                self.set_dc_voltage()
                self.set_rate()
                self.set_rmode()
                self.set_beep()
                
                # Start measurements
                self.start_measurements()
            else:
                self.show_error("Failed to connect")
                
        except Exception as e:
            self.show_error(f"Connection error: {e}")
    
    def disconnect_dmm(self):
        if self.update_id:
            self.root.after_cancel(self.update_id)
        
        self.dmm.close_serial_port()
        self.connect_btn.config(text="Connect", bg='#e74c3c')
        self.port_combo.config(state='normal')
        
        # Disable function buttons and config controls
        self.dc_voltage_btn.config(state='disabled')
        self.resistance_btn.config(state='disabled')
        self.diode_btn.config(state='disabled')
        self.cont_btn.config(state='disabled')
        self.cap_btn.config(state='disabled')
        self.rate_combo.config(state='disabled')
        self.rmode_combo.config(state='disabled')
        self.beep_combo.config(state='disabled')
        
        self.value_label.config(text="------")
        self.unit_label.config(text="")
        
        # Reset button colors
        self.dc_voltage_btn.config(bg='grey')
        self.resistance_btn.config(bg='grey')
        self.diode_btn.config(bg='grey')
        self.cont_btn.config(bg='grey')
        self.cap_btn.config(bg='grey')
    
    def set_dc_voltage(self):
        if self.dmm.set_dc_voltage():
            self.current_function = "DC Voltage"
            self.dc_voltage_btn.config(bg='#FFC300')  # Active color
            self.resistance_btn.config(bg='grey')
            self.diode_btn.config(bg='grey')
            self.cont_btn.config(bg='grey')
            self.cap_btn.config(bg='grey')
    
    def set_resistance(self):
        if self.dmm.set_resistance(self.rmode_var.get()):
            self.current_function = "Resistance"
            self.dc_voltage_btn.config(bg='grey')
            self.resistance_btn.config(bg='#FFC300')  # Active color
            self.diode_btn.config(bg='grey')
            self.cont_btn.config(bg='grey')
            self.cap_btn.config(bg='grey')
    
    def set_diode(self):
        if self.dmm.set_diode():
            self.current_function = "Diode"
            self.dc_voltage_btn.config(bg='grey')
            self.resistance_btn.config(bg='grey')
            self.diode_btn.config(bg='#FFC300')  # Active color
            self.cont_btn.config(bg='grey')
            self.cap_btn.config(bg='grey')

    def set_cont(self):
        if self.dmm.set_cont():
            self.current_function = "Cont"
            self.dc_voltage_btn.config(bg='grey')
            self.resistance_btn.config(bg='grey')
            self.diode_btn.config(bg='grey')
            self.cont_btn.config(bg='#FFC300')  # Active color
            self.cap_btn.config(bg='grey')

    def set_cap(self):
        if self.dmm.set_cap():
            self.current_function = "Cap"
            self.dc_voltage_btn.config(bg='grey')
            self.resistance_btn.config(bg='grey')
            self.diode_btn.config(bg='grey')
            self.cont_btn.config(bg='grey')
            self.cap_btn.config(bg='#FFC300')  # Active color
    
    def set_rate(self, event=None):
        rate_map = {"Slow": "S", "Medium": "M", "Fast": "F"}
        rate_char = rate_map.get(self.rate_var.get(), "M")
        self.dmm.set_rate(rate_char)
    
    def set_rmode(self, event=None):
        """Set resistance mode (2W or 4W)"""
        if self.dmm.is_connected and self.current_function == "Resistance":
            self.dmm.set_resistance(self.rmode_var.get())
    
    def set_beep(self, event=None):
        """Enable or disable beeper"""
        if self.dmm.is_connected:
            beep_enabled = (self.beep_var.get() == "ON")
            self.dmm.set_beep(beep_enabled)
    
    def start_measurements(self):
        if self.dmm.is_connected:
            try:
                value, unit = self.dmm.get_measurement()
                
                if value is not None:
                    self.value_label.config(text=value)
                    self.unit_label.config(text=unit)
                else:
                    self.value_label.config(text="ERROR")
                    self.unit_label.config(text="")
                    
            except Exception as e:
                print(f"Measurement error: {e}")
                self.value_label.config(text="ERROR")
                self.unit_label.config(text="")
            
            # Continue measurements every 200ms
            self.update_id = self.root.after(200, self.start_measurements)
    
    def show_error(self, message):
        self.value_label.config(text="ERROR")
        self.unit_label.config(text=message)
    
    def __del__(self):
        if self.dmm:
            self.dmm.close_serial_port()

def main():
    root = tk.Tk()
    app = OWONGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
