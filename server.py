import socket
from threading import Thread
from oscilloscope import Oscilloscope
import zlib

# 52113

class Server:

    def __init__(self, oscilloscope: Oscilloscope) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__host_ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
        self.__port = 9998
        self.client = None

        self.oscilloscope = oscilloscope

    def config_server(self) -> None:
        self.server.bind((self.__host_ip, self.__port))
        self.server.listen(1)
        print(f'LISTENING @ {self.__host_ip}:{self.__port}')
        (client, address) = self.server.accept()
        self.client = client
        print(f'CONNECTION FOUND @ {address}')

    def __send_message(self, message: str):
        encoded = bytes(message, 'utf-8')
        t1 = Thread(target=self.client.send, args=[zlib.compress(encoded)])
        t1.start()

    def __listen(self) -> None:
        while True:
            data = self.client.recv(2048).decode()

            if data:
                print(f'\nCLIENT > {data}')

                if "change time scale" in data:
                    scale = float(data.split(':')[1])
                    message = self.oscilloscope.change_time_scale(scale)
                    self.__send_message(message)
                elif "change time offset" in data:
                    offset = float(data.split(':')[1])
                    message = self.oscilloscope.change_time_offset(offset)
                    self.__send_message(message)
                elif "change vertical scale" in data:
                    channel = int(data.split(':')[1])
                    scale = float(data.split(':')[2])
                    message = self.oscilloscope.change_vertical_scale(channel, scale)
                    self.__send_message(message)
                elif "change samples per read" in data:
                    samples_per_read = int(data.split(':')[1])
                    message = self.oscilloscope.change_samples_per_read(samples_per_read)
                    self.__send_message(message)
                elif "change sampling rate" in data:
                    rate = int(data.split(':')[1])
                    message = self.oscilloscope.change_sampling_rate(rate)
                    self.__send_message(message)
                elif "auto setup" in data:
                    message = self.oscilloscope.auto_setup()
                    self.__send_message(message)
                elif "exit" in data:
                    message = self.oscilloscope.exit()
                    self.__send_message(message)
                elif "set trigger source:" in data:
                    channel = int(data.split(':')[1])
                    message = self.oscilloscope.change_trigger_source(channel)
                    self.__send_message(message)
                elif "set trigger level:" in data:
                    level = float(data.split(':')[1])
                    message = self.oscilloscope.change_trigger_level(level)
                    self.__send_message(message)
                elif "set trigger coupling:" in data:
                    couple = data.split(':')[1]
                    message = self.oscilloscope.change_trigger_coupling(couple)
                    self.__send_message(message)
                elif "set trigger slope:" in data:
                    slope = data.split(':')[1]
                    message = self.oscilloscope.change_trigger_slope(slope)
                    self.__send_message(message)
                elif "change trigger mode" in data:
                    mode = data.split(':')[1]
                    message = self.oscilloscope.change_trigger_mode(mode)
                    self.__send_message(str(message))
                elif "read once" in data:
                    channel, measurement = self.oscilloscope.read_once(int(data.split(':')[1]))
                    mes_str = str(measurement)
                    mes = f'[C-{channel}]:{mes_str}'
                    self.__send_message(mes)
                elif 'read trigger' in data:
                    ch1_measurement, ch2_measurement = self.oscilloscope.read_around_trigger()
                    self.__send_message(f'[C-1]:{str(ch1_measurement)}')
                    self.__send_message(f'[C-2]:{str(ch2_measurement)}')
                else:
                    self.__send_message('[ERROR]: Invalid Command')

    def start(self):
        self.__listen()
 

if __name__ == '__main__':
    print(socket.gethostbyname_ex(socket.gethostname()))
    scope = Oscilloscope()
    server_socket = Server(scope)
    server_socket.config_server()
    server_socket.start()
