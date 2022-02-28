import socket
from threading import Thread
from datetime import datetime, date
import zlib

class Client:

    def __init__(self, server_ip: str, server_port: int):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_ip = server_ip
        self.__port = server_port

        run_date = str(date.today())
        run_time = str(datetime.now().time()).split('.')[0].split(':')
        self.timestamp = f'{run_date}_{run_time[0]}_{run_time[1]}'

        with open(f'channel_1_{self.timestamp}.txt', 'a') as f:
            f.write(f'Channel 1 - {self.timestamp}\n')
        with open(f'channel_2_{self.timestamp}.txt', 'a') as f:
            f.write(f'Channel 2 - {self.timestamp}\n')
        with open(f'client_logs_{self.timestamp}.txt', 'a') as f:
            f.write(f'Started @ {self.timestamp} \n')
        
        self.ch1_data = None
        self.ch2_data = None

        # Default Scope Values
        self.time_scale = 1.0
        self.horizontal_offset = 0.0
        self.c1_vertical_scale = 1.0
        self.c2_vertical_scale = 1.0
        self.samples = 20000
        self.sampling_rate = 1000000  # 1MHz
        self.trigger_source = 1
        self.trigger_level = 1
        self.trigger_coupling = "ac"
        self.trigger_slope = 'positive'
        self.trigger_mode = 'auto'

    def config(self):
        try:
            self.__client.connect((self.__server_ip, self.__port))
        except Exception as e:
            print(e)

    def __listen_for_message(self):
        while True:
            data = self.__client.recv(1000000000)
            if data:

                data = zlib.decompress(data)
                data = data.decode('utf-8')

                if "[C-1]" in data:
                    measurement = data.split(':')[1]
                    self.ch1_data = measurement
                    self.__write_measurement_to_file(1, measurement)
                elif "[C-2]" in data:
                    measurement = data.split(':')[1]
                    self.ch2_data = measurement
                    self.__write_measurement_to_file(2, measurement)
                elif "[ERROR]" in data:
                    print(data.split(':')[1])
                elif "[INFO]" in data:
                    print(data)
                    if '[C1-Vertical Scale]' in data:
                        self.c1_vertical_scale = float(data.split(":")[1])
                    elif '[C2-Vertical Scale]' in data:
                        self.c2_vertical_scale = float(data.split(":")[1])
                    elif '[Time Scale]' in data:
                        self.time_scale = float(data.split(':')[1])
                    elif '[Samples]' in data:
                        self.samples = int(data.split(':')[1])
                    elif '[Sampling Rate]' in data:
                        self.sampling_rate = int(data.split(':')[1])
                    elif '[Trigger Source]' in data:
                        self.trigger_source = data.split(':')[1]
                    elif '[Trigger Level]' in data:
                        self.trigger_level = float(data.split(':')[1])
                    elif '[Trigger Coupling]' in data:
                        self.trigger_coupling = data.split(':')[1]
                    elif '[Trigger Slope]' in data:
                        self.trigger_slope = data.split(':')[1]
                    elif '[Trigger Mode]' in data:
                        self.trigger_mode = data.split(':')[1]
                    elif '[Horizontal Offset]' in data:
                        self.horizontal_offset = float(data.split(':')[1])
                else:
                    print('Invalid return message')

    def __write_measurement_to_file(self, channel: int, data):
        def write():
            try:
                if channel == 1:
                    with open(f'channel_1_{self.timestamp}.txt', 'a') as f:
                        f.write(data)
                elif channel == 2:
                    with open(f'channel_2_{self.timestamp}.txt', 'a') as f:
                        f.write(data)
                else:
                    print('Invalid channel')

                print(f'channel {channel} data written to file')
            except Exception as e:
                print(f'Could not write {channel} to file')

        t1 = Thread(target=write)
        t1.start()

    def __send_message_dev(self):
        while True:
            message = input('MESSAGE > ')
            message = message.strip()
            self.send_message(message)

    def send_message(self, message: str):
        try:
            message = message.strip()

            run_date = str(date.today())
            run_time = str(datetime.now().time()).split('.')[0]
            timestamp = f'{run_date}_{run_time}'
            
            with open(f'client_logs_{self.timestamp}.txt', 'a') as f:
                f.write(f'[{timestamp}]: {message}\n')

            self.__client.send(message.encode())
        except Exception as e:
            print('Could not send message')

    def start_dev(self):
        t1 = Thread(target=self.__listen_for_message)
        t2 = Thread(target=self.__send_message_dev)
        t1.start()
        t2.start()

    def start(self):
        t1 = Thread(target=self.__listen_for_message)
        t1.start()


if __name__ == '__main__':
    client = Client('172.25.1.2', 9998)
    client.config()
    client.start_dev()
