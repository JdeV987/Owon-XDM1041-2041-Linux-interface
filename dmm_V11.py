#  https://www.1001fonts.com/search.html?search=lcd
#  https://kidspattern.com/color/

#  Author: JHT (Joe's Hobby Tech)     
#  https://www.youtube.com/@joeshobbytech    
#  https://github.com/JdeV987?tab=repositories

#  Credits: 95% DeepSeek AI  ;)
#  Date:30/09/202
#  Version: 1.1

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

    def set_dc_current(self):
        """Set to DC Current mode"""
        self.current_mode = 'current'
        return self.send_command("CONF:CURR:DC")
    
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
    
##************************************************************##

    def get_measurement(self):
        """Get current measurement value"""
        try:
            if not self.ser or not self.ser.is_open:
                return None, None
                
            command = b'MEAS:SHOW?\n'
            self.ser.write(command)
            response = self.ser.readline().strip()
            response_text = response.decode('utf-8', errors='ignore').strip()
            
          #  print(f"Raw DMM MEAS:SHOW?: '{response_text}'")  # Debug


#*****************************************************************************

            command = b'MEAS1?\n'
            self.ser.write(command)
            response = self.ser.readline().strip()
            response_text = response.decode('utf-8', errors='ignore').strip()
            
         #   print(f"Raw DMM MEAS1?: '{response_text}'")  # Debug



#****************************************************************************
                
            # Parse the value and unit separately
            numeric_value, unit_text = self._parse_measurement_value(response_text)

            # Handle overload case - return "OPEN" for diode, "OVERLOAD" for others

            if numeric_value == 'overload':
                if self.current_mode == 'cont':
               # if self.current_mode in ("cont"):
                    return '', 'OPEN'
              #  else:
              #      return '', 'OVERLOAD'

            if numeric_value == 'open':
                if self.current_mode == 'diode': 
               # if self.current_mode in ("diode"): 
                    return '', 'OPEN'
               # else:
               #     return '', 'OVERLOAD'

            if numeric_value == 'overload':
               if self.current_mode == "resistance": 
                    return '', 'OVERLOAD'
            


            # Special handling for resistance - auto-scale units
            if (self.current_mode == 'resistance' or self.current_mode == 'cont' or 
                'Ω' in unit_text or unit_text in ['M', 'k']):
                try:
                    float_value = float(numeric_value)
                    # Auto-scale resistance to appropriate units
                    if float_value >= 1e6:  # 1 MΩ and above
                        scaled_value = float_value / 1e6
                        unit = 'MΩ'
                    elif float_value >= 1e3:  # 1 kΩ to 999 kΩ
                        scaled_value = float_value / 1e3
                        unit = 'kΩ'
                    else:  # Below 1 kΩ (Ω range)
                        scaled_value = float_value
                        unit = 'Ω'
                    
                    # Format the scaled value with proper decimal places
                    if unit == 'MΩ':
                        # MΩ: always show 4 decimal places
                        formatted_value = f"{scaled_value:.4f}".rstrip('0').rstrip('.')
                        # Ensure we have at least one digit after decimal if it's a decimal number
                        if '.' in formatted_value and len(formatted_value.split('.')[1]) == 0:
                            formatted_value += '0'
                    elif unit == 'kΩ':
                        # kΩ: use 4 decimals for values < 50 kΩ, 3 decimals for values ≥ 100 kΩ
                        if scaled_value >= 50:
                            formatted_value = f"{scaled_value:.3f}".rstrip('0').rstrip('.')
                        else:
                            formatted_value = f"{scaled_value:.4f}".rstrip('0').rstrip('.')
                        # Ensure we have at least one digit after decimal if it's a decimal number
                        if '.' in formatted_value and len(formatted_value.split('.')[1]) == 0:
                            formatted_value += '0'
                    else:  # Ω
                        # Ω: adaptive decimal places with special handling for 4-wire mode < 1Ω
                        if scaled_value >= 1000:  # 1000-9999Ω
                            formatted_value = f"{scaled_value:.0f}"
                        elif scaled_value >= 100:  # 100-999Ω - show 2 decimals
                            formatted_value = f"{scaled_value:.2f}"
                        elif scaled_value >= 10:   # 10-99Ω - show 2 decimals
                            formatted_value = f"{scaled_value:.2f}"
                        elif scaled_value >= 1:    # 1-9Ω - show 3 decimals
                            formatted_value = f"{scaled_value:.3f}"
                        else:                      # 0-1Ω - show 4 decimals, especially for 4-wire
                            formatted_value = f"{scaled_value:.4f}"
                    
                    return formatted_value, f" {unit}"
                    
                except (ValueError, TypeError):
                    # If conversion fails, fall through to normal processing
                 pass



            # Special handling for diode - auto-scale units 
            if (self.current_mode == 'diode' or 'VDC' in unit_text): #or unit_text in ['mVDC','VDC']):
                try:
                 #   print(f"DEBUG: Processing diode - numeric_value='{numeric_value}'")
                    float_value = float(numeric_value)
                 #   print(f"DEBUG: float_value={float_value}")
                    
                    # Auto-scale diode to appropriate units
                    if float_value >= 1:  # 1 V and above
                       scaled_value = float_value
                       unit = 'VDC'

                    else:  # Below 1 V - show in mV
                        scaled_value = float_value #* 1000  # Convert V to mV
                        unit = 'VDC'
                        # Format to 4 decimal places, properly handling the rounding
                        formatted_value = f"{scaled_value:.4f}"

 
                    
                 #   print(f"DEBUG: scaled_value={scaled_value}, unit={unit}")
                    
                    # Format the scaled value with proper decimal places
                    if unit == 'VDC':
                        # For mV, always show 4 decimals
                        formatted_value = f"{scaled_value:.4f}"
                    
                    
                 #   print(f"DEBUG: Returning '{formatted_value}', '{unit}'")
                    return formatted_value, f" {unit}"
                    
                except (ValueError, TypeError) as e:
                 #   print(f"DEBUG: Current scaling error: {e}")
                    # If conversion fails, fall through to normal processing
                    pass



            
            # Special handling for capacitance - auto-scale units
            if self.current_mode == 'cap' or 'F' in unit_text:
                try:
                    float_value = float(numeric_value)
                    # Auto-scale capacitance to appropriate units
                    if float_value >= 1e-3:  # 1,000 uF and above
                        scaled_value = float_value / 1e-3
                        unit = 'mF'
                    elif float_value >= 1e-6:  # 1 uF to 999 uF
                        scaled_value = float_value / 1e-6
                        unit = 'uF'
                    elif float_value >= 1e-9:  # 1 nF to 999 nF
                        scaled_value = float_value / 1e-9
                        unit = 'nF'
                    else:  # Below 1 nF (pF range)
                        scaled_value = float_value / 1e-12
                        unit = 'pF'
                    
                    # Format the scaled value with proper decimal places
                    if scaled_value >= 1000:
                        formatted_value = f"{scaled_value:.0f}"
                    elif scaled_value >= 100:
                        formatted_value = f"{scaled_value:.1f}"
                    elif scaled_value >= 10:
                        formatted_value = f"{scaled_value:.2f}"
                    else:
                        formatted_value = f"{scaled_value:.3f}"
                    
                    return formatted_value, f" {unit}"
                    
                except (ValueError, TypeError):
                    # If conversion fails, fall through to normal processing
                    pass
 

           

            # Special handling for current - auto-scale units (THIS MUST COME FIRST)
            if (self.current_mode == 'current' or 
                'A' in unit_text or unit_text in ['uADC', 'mADC', 'ADC']):
                try:
                   # print(f"DEBUG: Processing current - numeric_value='{numeric_value}'")
                    float_value = float(numeric_value)
                  #  print(f"DEBUG: float_value={float_value}")
                    
                    # Auto-scale current to appropriate units
                    if float_value >= 1:  # 1 A and above
                        scaled_value = float_value
                        unit = 'ADC'
                    elif float_value >= 1e-3:  # 1 mA to 999 mA
                        scaled_value = float_value / 1e-3
                        unit = 'mADC'
                    elif float_value >= 1e-6:  # 1 uA to 999 uA
                        scaled_value = float_value / 1e-6
                        unit = 'uADC'
                    else:  # Below 1 uA (nA range)
                        scaled_value = float_value / 1e-9
                        unit = 'nADC'
                    
                   # print(f"DEBUG: scaled_value={scaled_value}, unit={unit}")
                    
                    # Format the scaled value with proper decimal places
                    if unit == 'uADC' or unit == 'mADC':
                        # For uA and mA, always show 2 decimals
                        formatted_value = f"{scaled_value:.2f}"
                    else:
                        # For A and nA, use adaptive formatting
                        if scaled_value >= 1000:
                            formatted_value = f"{scaled_value:.0f}"
                        elif scaled_value >= 100:
                            formatted_value = f"{scaled_value:.1f}"
                        elif scaled_value >= 10:
                            formatted_value = f"{scaled_value:.2f}"
                        else:
                            formatted_value = f"{scaled_value:.3f}"
                    
                 #   print(f"DEBUG: Returning '{formatted_value}', '{unit}'")
                    return formatted_value, f" {unit}"
                    
                except (ValueError, TypeError) as e:
                #    print(f"DEBUG: Current scaling error: {e}")
                    # If conversion fails, fall through to normal processing
                    pass



            # Special handling for voltage - auto-scale units (THIS MUST COME FIRST)
            if (self.current_mode == 'voltage' or 
                'VDC' in unit_text or unit_text in ['mVDC','VDC']):
                try:
                 #   print(f"DEBUG: Processing voltage - numeric_value='{numeric_value}'")
                    float_value = float(numeric_value)
                 #   print(f"DEBUG: float_value={float_value}")
                    
                    # Auto-scale voltage to appropriate units
                    if float_value >= 1:  # 1 V and above
                        scaled_value = float_value
                        unit = 'VDC'
                    #else:
                    #    scaled_value = float_value / 1e-3        # 1 mV to 999 mV
                    #    unit = 'mV'


                    else:  # Below 1 V - show in mV
                        scaled_value = float_value * 1000  # Convert V to mV
                        unit = 'mVDC'
                        # Format to 4 decimal places, properly handling the rounding
                        formatted_value = f"{scaled_value:.4f}"

 
                    
                 #   print(f"DEBUG: scaled_value={scaled_value}, unit={unit}")
                    
                    # Format the scaled value with proper decimal places
                   # if unit == 'mVDC':
                        # For mV, always show 3 decimals
                   #     formatted_value = f"{scaled_value:.3f}"
                   # else:
                        # For V,use adaptive formatting
                    if scaled_value >= 1000:
                        formatted_value = f"{scaled_value:.1f}"
                    elif scaled_value >= 100:
                        formatted_value = f"{scaled_value:.2f}"
                    elif scaled_value >= 10:
                        formatted_value = f"{scaled_value:.3f}"
                    elif scaled_value >= 1:
                        formatted_value = f"{scaled_value:.4f}"
                    elif scaled_value < 1:
                        formatted_value = f"{scaled_value:.2f}"
                    elif scaled_value < 0.1:
                        formatted_value = f"{scaled_value:.3f}"
                    else:
                        formatted_value = f"{scaled_value:.3f}"
                
                 #   print(f"DEBUG: Returning '{formatted_value}', '{unit}'")
                    return formatted_value, f" {unit}"
                    
                except (ValueError, TypeError) as e:
                 #   print(f"DEBUG: Current scaling error: {e}")
                    # If conversion fails, fall through to normal processing
                    pass




            # Use the unit text to determine what unit to display
            if unit_text in ['mVDC', 'VDC', 'uADC', 'mADC', 'A', 'Ω', 'M', 'k', 'nF', 'uF', 'mF', 'open', 'overload']:
                if unit_text == 'mVDC':
                    return numeric_value, ' mVDC'
                elif unit_text == 'VDC':
                    return numeric_value, ' VDC'
                elif unit_text == 'uADC':
                    return numeric_value, ' uADC'
                elif unit_text == 'mADC':
                    return numeric_value, ' mADC'
                elif unit_text == 'ADC':
                    return numeric_value, ' ADC'
                elif unit_text == 'Ω':
                    return numeric_value, ' Ω'
                elif unit_text == 'k':
                    return numeric_value, ' kΩ'
                elif unit_text == 'M':
                    return numeric_value, ' MΩ'
                elif unit_text == 'nF':
                    return numeric_value, ' nF'
                elif unit_text == 'uF':
                    return numeric_value, ' uF'
                elif unit_text == 'mF':
                    return numeric_value, ' mF'
                elif unit_text == 'open':
                    return numeric_value, 'OPEN'
                elif unit_text == 'overload':
                    return 'OVERLOAD', 'OVERLOAD'

            else:
                # Fallback to current mode if unit text not recognized
                if self.current_mode == 'resistance':
                    return numeric_value, ' Ω'
                elif self.current_mode == 'cont':
                    return numeric_value, ' Ω'
                elif self.current_mode == 'voltage':
                    return numeric_value, ' VDC'
                elif self.current_mode == 'current':
                    return numeric_value, ' ADC'
                elif self.current_mode == 'diode':
                    return numeric_value, ' VDC'
                else:
                    return numeric_value, unit_text
                        
        except Exception as e:
            print(f"Measurement error: {e}")
            return None, None

    
#****************************************************************

    def _parse_measurement_value(self, response_text):
        """
        Parse measurement value like '10.234VDC' or '9.532182E+00' into (value, unit)
        Remove leading zeros from the numeric value and limit to 4 decimal places
        Handle overload conditions for resistance, diode test and current.
        """
        try:
            # Handle overload case first
            if 'overload' in response_text.lower():
                return 'overload', ''
            
            # Find where numbers end and unit begins
            for i, char in enumerate(response_text):
                if not char.isdigit() and char not in ['.', '-', '+', 'E', 'e']:
                    numeric_value = response_text[:i]
                    unit_text = response_text[i:]
                    
                    # For current measurements, preserve scientific notation for scaling
                    if self.current_mode == 'current' or 'A' in unit_text:
                        # Don't format current values - let the scaling handle it
                        return numeric_value, unit_text

                    # For voltage measurements, preserve scientific notation for scaling
                    if self.current_mode == 'voltage' or 'V' in unit_text:
                        # Don't format current values - let the scaling handle it
                        return numeric_value, unit_text

                    # For diode test, preserve scientific notation for scaling
                    if self.current_mode == 'diode' or 'V' in unit_text:
                        # Don't format current values - let the scaling handle it
                        return numeric_value, unit_text

                    # Check for resistance overload (extremely large numbers in resistance mode)
                    if (self.current_mode == 'resistance' or self.current_mode == 'cont' or 
                        'Ω' in unit_text or unit_text in ['M', 'k']):
                        try:
                            float_value = float(numeric_value)
                            # If resistance value is extremely large, treat as overload
                            if float_value > 1e8:  # 100,000,000 Ω
                                return 'overload', ''
                        except ValueError:
                            pass
                    
                    # Check for diode test overload (open circuit)
                    elif self.current_mode == 'diode':
                        try:
                            float_value = float(numeric_value)
                            # If diode voltage is extremely high, treat as open circuit
                            if float_value > 1e8:  # 100,000,000 V
                                return 'open', ''
                        except ValueError:
                            pass
                        
                    # Process numeric value (handle scientific notation and limit decimals)
                    numeric_value = self._format_numeric_value(numeric_value)
                    
                    return numeric_value, unit_text

            # If no unit found
            numeric_value = response_text
  


           # Check for overload in numeric value only (no unit case)
            if self.current_mode == 'resistance' or self.current_mode == 'cont':
                try:
                    float_value = float(numeric_value)
                    if float_value > 1e8:
                        return 'overload', ''
                except ValueError:
                    pass
            elif self.current_mode == 'diode':
                try:
                    float_value = float(numeric_value)
                    if float_value > 1e8:
                        return 'open', ''
                except ValueError:
                    pass
                    
            return numeric_value, ''
                
        except Exception as e:
            print(f"Parse error: {e}")
            return response_text, ''


#*************************************************************************



    def _format_numeric_value(self, value_str):
        """
        Format numeric value: handle scientific notation, limit to 4 decimal places for most modes,
        but preserve full precision for capacitance measurements
        """
        try:
            # Convert to float to handle scientific notation and normalize
            float_value = float(value_str)
            
            # Special handling for capacitance - preserve full precision
            if self.current_mode == 'cap':
                # For capacitance, we want to preserve small values like 0.000000001 (1pF)
                # Use more decimal places for capacitance
                formatted = f"{float_value:.11f}"
                # Remove trailing zeros but keep the decimal precision for small values
                if '.' in formatted:
                    formatted = formatted.rstrip('0')
                    # If we removed all decimals, remove the decimal point too
                    if formatted.endswith('.'):
                        formatted = formatted[:-1]
            else:
                # For other modes, limit to 4 decimal places
                formatted = f"{float_value:.4f}"
                # Remove trailing zeros and decimal point if not needed
                if '.' in formatted:
                    formatted = formatted.rstrip('0').rstrip('.')
            
            # Ensure there's a leading zero for values less than 1
            if formatted.startswith('.'):
                formatted = '0' + formatted
            elif formatted.startswith('-.'):
                formatted = '-0' + formatted[1:]
                
            return formatted
        except ValueError:
            # If conversion fails, use original with proper zero handling
            result = self._remove_leading_zeros(value_str)
            # Ensure leading zero for decimal values
            if result.startswith('.'):
                result = '0' + result
            elif result.startswith('-.'):
                result = '-0' + result[1:]
            return result



#*************************************************************************




    def _remove_leading_zeros(self, value_str):
        """
        Remove leading zeros from a numeric string while preserving formatting
        Examples:
            "09.123" -> "9.123"
            "00.456" -> "0.456"
            "000.123" -> "0.123"
            "123.456" -> "123.456"
            "-09.123" -> "-9.123"
        """
        if not value_str:
            return value_str
        
        # Handle negative numbers
        is_negative = value_str.startswith('-')
        if is_negative:
            value_str = value_str[1:]
        
        # Handle decimal numbers
        if '.' in value_str:
            integer_part, decimal_part = value_str.split('.')
            # Remove leading zeros but keep at least one digit
            integer_part = integer_part.lstrip('0') or '0'
            result = f"{integer_part}.{decimal_part}"
        else:
            # Handle integers
            result = value_str.lstrip('0') or '0'
        
        # Restore negative sign if needed
        if is_negative and result != '0':
            result = '-' + result
        
        return result
        

#*****************************************************************

    def get_range(self):
        """Get current measurement range"""
        try:
            if not self.ser or not self.ser.is_open:
                return None, None
                
            # First check if auto-ranging is enabled
            command = b'AUTO?\n'
            self.ser.write(command)
            response = self.ser.readline().strip()
            auto_response = response.decode('utf-8', errors='ignore').strip()
            
            is_auto = (auto_response == '1')
            
            # Get the actual range value
            command = b'RANGE?\n'
            self.ser.write(command)
            response = self.ser.readline().strip()
            range_value = response.decode('utf-8', errors='ignore').strip()
            
           # print(f"Auto response: '{auto_response}', Range response: '{range_value}'")  # Debug
            
            return is_auto, range_value
                
        except Exception as e:
            print(f"Range query error: {e}")
            return True, "Auto"  # Default to auto if error

    def get_range_with_units(self):
        """Get range with specific units based on current mode"""
        try:
            is_auto, range_value = self.get_range()
            
            if is_auto:
                # For auto range, show "A: [range_value]"
                return f"[A] {range_value}"
            else:
                # For manual range, show "M: [range_value]" 
                return f"[M] {range_value}"
            
        except Exception as e:
            print(f"Range units error: {e}")
            return "A: Auto"


#***************************************************************


    def is_connected(self):
        """Check if multimeter is connected"""
        return self.is_connected and self.ser and self.ser.is_open
