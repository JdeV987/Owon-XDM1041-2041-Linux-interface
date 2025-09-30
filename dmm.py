# V1.0
import serial
import serial.tools.list_ports
import time

class OWONXDM2041:
    def __init__(self, serial_port=None, baud_rate=115200):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.ser = None
        self.is_connected = False
        self.current_mode = 'voltage'  # Track current mode for fallback
        self.resistance_mode = '2W'    # 2W or 4W resistance mode
        self.beep_enabled = False      # Beep status
        
    def get_available_ports(self):
        """Get list of available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["No ports available"]
    
    def open_serial_port(self, port=None):
        """Open connection to multimeter"""
        try:
            if port:
                self.serial_port = port
                
            if not self.serial_port:
                raise ValueError("No serial port specified")
                
            self.ser = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Wait for connection to establish
            time.sleep(2)
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"Error opening serial port: {e}")
            self.is_connected = False
            return False
    
    def close_serial_port(self):
        """Close connection to multimeter"""
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.is_connected = False
            return True
        except Exception as e:
            print(f"Error closing serial port: {e}")
            return False
    
    def send_command(self, command):
        """Send SCPI command to multimeter"""
        try:
            if not self.ser or not self.ser.is_open:
                return False
                
            cmd = command + '\n'
            self.ser.write(cmd.encode())
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def query(self, command):
        """Send query and return response"""
        try:
            if not self.ser or not self.ser.is_open:
                return None
                
            cmd = command + '\n'
            self.ser.write(cmd.encode())
            time.sleep(0.2)
            response = self.ser.readline().decode('utf-8', errors='ignore').strip()
            return response
        except Exception as e:
            print(f"Error querying: {e}")
            return None
    
    def get_idn(self):
        """Get multimeter identification"""
        return self.query("*IDN?")
    
    def set_dc_voltage(self):
        """Set to DC Voltage mode"""
        self.current_mode = 'voltage'
        return self.send_command("CONF:VOLT:DC")
    
    def set_resistance(self, mode='2W'):
        """Set to Resistance mode (2W or 4W)"""
        self.current_mode = 'resistance'
        self.resistance_mode = mode
        if mode == '4W':
            return self.send_command("CONF:FRES")  # 4-wire resistance
        else:
            return self.send_command("CONF:RES")   # 2-wire resistance
    
    def set_diode(self):
        """Set to Diode mode"""
        self.current_mode = 'diode'
        return self.send_command("CONF:DIOD")

    def set_cont(self):
        """Set to Conyinuity mode"""
        self.current_mode = 'cont'
        return self.send_command("CONF:CONT")

    def set_cap(self):
        """Set to Capacitor mode"""
        self.current_mode = 'cap'
        return self.send_command("CONF:CAP")
    
    def set_rate(self, rate):
        """Set measurement rate (S=Slow, M=Medium, F=Fast)"""
        rate = rate.upper()
        if rate in ['S', 'M', 'F']:
            return self.send_command(f"RATE {rate}")
        return False
    
    def set_beep(self, enabled):
        """Enable or disable beeper"""
        self.beep_enabled = enabled
        if enabled:
            return self.send_command("SYST:BEEP:STAT ON")
        else:
            return self.send_command("SYST:BEEP:STAT OFF")
    
    def get_measurement(self):
        """Get current measurement value"""
        try:
            if not self.ser or not self.ser.is_open:
                return None, None
                
            command = b'MEAS:SHOW?\n'
            self.ser.write(command)
            response = self.ser.readline().strip()
            response_text = response.decode('utf-8', errors='ignore').strip()
            
           # print(f"Raw DMM response: '{response_text}'")  # Debug
            
            # Parse the value and unit separately
            numeric_value, unit_text = self._parse_measurement_value(response_text)

            if numeric_value == 'overload':
                return numeric_value, 'OVERLOAD'
            
            # Use the unit text to determine what unit to display
            if unit_text in ['mVDC', 'VDC', 'Ω', 'M', 'k', 'nF', 'uF', 'F', 'open', 'overload']:
                if unit_text == 'mVDC':
                    return numeric_value, ' mVDC'
                elif unit_text == 'VDC':
                    return numeric_value, ' VDC'
                elif unit_text == 'Ω':
                    return numeric_value, ' Ω'
                elif unit_text == 'k':
                    return numeric_value, ' kΩ'
                elif unit_text == 'M':
                    return numeric_value, ' MΩ'
                elif unit_text == 'nF':
                    return numeric_value, ' nF'
                elif unit_text == 'F':
                    return numeric_value, ' uF'
                elif unit_text == 'open':
                    return numeric_value, 'OPEN'
                elif unit_text == 'overload':
                    return numeric_value, 'OVERLOAD'


            else:
                # Fallback to current mode if unit text not recognized
                if self.current_mode == 'resistance':
                    return numeric_value, ' Ω'
                elif self.current_mode == 'cont':
                    return numeric_value, ' Ω'
                elif self.current_mode == 'voltage':
                    return numeric_value, ' VDC'
             #   elif self.current_mode == 'cap':
              #      return numeric_value, 'F'
                elif self.current_mode == 'diode':
                    return numeric_value, ' V'  # Diode mode typically shows voltage
                else:
                    return numeric_value, unit_text
                    
        except Exception as e:
            print(f"Measurement error: {e}")
            return None, None
    
    def _parse_measurement_value(self, response_text):
        """
        Parse measurement value like '10.234VDC' into (value, unit)
        """
        try:
            # Handle overload case
           # if 'overload' in response_text.lower():
           #     return '', ''
            
            # Find where numbers end and unit begins
            for i, char in enumerate(response_text):
                if not char.isdigit() and char not in ['.', '-', '+']:
                    numeric_value = response_text[:i]
                    unit_text = response_text[i:]
                    return numeric_value, unit_text
            
            # If no unit found, return entire text as numeric value
            return response_text, ''
                
        except Exception as e:
            print(f"Parse error: {e}")
            return response_text, ''
    
    def is_connected(self):
        """Check if multimeter is connected"""
        return self.is_connected and self.ser and self.ser.is_open
