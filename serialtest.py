import serial
import serial.tools.list_ports
import time
ser= serial.Serial("COM3",115200)
while(1):
    print(1)
    data = ser.read().decode()
    print(data, end="")
 #   time.sleep(0.1)
    
