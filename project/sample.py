import wave
import numpy as np
import serial
import serial.tools.list_ports
import csv
from matplotlib import pyplot
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
class serialAudio:
    def __init__(self,comPort="COM3",buad=115200,sampleRate=10000):
        print("Connecting to STM...")
        devices = serial.tools.list_ports.comports()
        for device in devices:
            print(device)
            comPort = str(device)[0:4]
        
        self.ser = serial.Serial(comPort,str(buad))
        self.ser.timeout = 0.1
        self.data_list = []
        self.last3 = [0,255,0]
        self.sampleRate = 10000
    
    def receive_data(self,time):
        for i in range(self.sampleRate * time):
            sample = self.ser.read()

            self.data_list.append(sample[0])
        print(self.data_list)
    
    def receive_data_unbounded(self):
        while(1):
            sample = self.ser.read()
            if len(sample)!=0:
                self.data_list.append(sample[0])

            # if self.data_list[-4:-1] == self.last3:
            #     for i in range(3):
            #         self.data_list.pop()
            #     break
        

    def generate_wav(self, file_name):
        data = np.array(self.data_list)

        data = (data-data.min())/data.max()
        data = data*255
        data = data.astype(np.uint8)
        
        with wave.open(file_name,'wb') as wav_file:
            print(data)

            wav_file.setnchannels(1)
            wav_file.setsampwidth(1)
            wav_file.setframerate(self.sampleRate)
            wav_file.writeframes(data.tobytes())
            print(data)

    def generate_csv(self, filename):
        with open(f"{filename}.csv","w") as csvfile:
            feildnames = ["Sample Rate", "Data"]
            writer = csv.writer(csvfile)
            writer.writerow(feildnames)
            for datapoint in self.data_list:
                writer.writerow([self.sampleRate,datapoint])

    def generate_plot(self):
        time  = np.arange(0,len(self.data_list)/self.sampleRate,1/self.sampleRate)

        pyplot.plot(time,self.data_list)
        pyplot.savefig("waveform.png",dpi=100)

class serialAudioController(serialAudio):
    def __init__(self, comPort="COM3", buad=115200, sampleRate=10000):
        super().__init__(comPort, buad, sampleRate)

    def main_menu(self):
        while(1):
            clear_screen()
            print("1. Manual Recording mode\n2. Distance measureing mode\n3. Generate outputs")
            userinput = int(input("Enter option: "))
            if userinput==1:
                self.manual()
            elif userinput==2:
                self.distance()
            elif userinput == 3:
                self.generate_ouputs()
            elif userinput == 4:
                print(self.data_list)
            elif userinput == 5:
                self.change()


    def change(self):
        new = int(input("Enter new sample rate: "))
        self.sampleRate = new

    def manual(self):
        self.ser.write(bytes.fromhex("00"))
        clear_screen()
        self.data_list = []
        time = int(input("Enter time to record for (s): "))
        print("Recording data")
        self.receive_data(time)
        print("Data recorded sucsessfully")
    
    def distance(self):
        self.ser.write(bytes.fromhex("01"))
        print("Entering distance based measurement mode\nPress Crtl+C to exit")
        try:
            self.receive_data_unbounded()
        except KeyboardInterrupt:
            print("Data recorded sucsessfully")

    def generate_ouputs(self):
        clear_screen()
        print("1. Audio file\n2. Waveform Image\n3. csv file")
        userinput = int(input("Enter option:"))
        if userinput==1:
            self.generate_wav("output.wav")
        elif userinput == 2:
            self.generate_plot()
        elif userinput == 3:
            self.generate_csv("output")


if __name__=="__main__":
    interface = serialAudioController()
    interface.main_menu()
