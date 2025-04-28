import serial
import serial.tools.list_ports
import time
devices = serial.tools.list_ports.comports()
for device in devices:
    print(device)
ser= serial.Serial("COM3",115200)

ser.write(ord("S"))
    
