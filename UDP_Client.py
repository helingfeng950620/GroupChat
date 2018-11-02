import socket
import threading


class GroupChatClient_UDP:
    def __init__(self, ip='127.0.0.1', port=9999):
        self.address = ip, port
        self.event = threading.Event()
        self.lock = threading.Lock()
        self.client = socket.socket(type=socket.SOCK_DGRAM)

    def start(self):
        """
        Start a client program.
        """
        self.client.connect(self.address)
        self.client.send(b'')
        threading.Thread(target=self.heartbeat, name='heartbeat', daemon=True).start()
        threading.Thread(target=self.read, name='read', daemon=True).start()
        threading.Thread(target=self.write, name='write', daemon=True).start()
        threading.Thread(target=self.terminate, name='terminate').start()

    def read(self):
        """
        Be ready to receive the message from other clients.
        """
        while True:
            try:
                data, server_address = self.client.recvfrom(1024)
                print('{}:{}  :\t{}'.format(server_address[0], server_address[1], data.decode()))
            except Exception:
                self.quit()

    def write(self):
        """
        Be ready to send the content from input function to other clients.
        """
        while True:
            data = input('>>>')
            if data == 'quit':
                self.quit()
                break
            address = self.client.getsockname()
            print('{}:{}  :\t{}'.format(address[0], address[1], data))
            self.client.send(data.encode())

    def heartbeat(self):
        """
        Due to the UDP protocol,
        client program need to send heart beat package to ensure the connection with server.
        """
        while not self.event.wait(5):  # 注意这里是返回False, 要进循环, 加一个not
            self.client.send(b'')

    def quit(self):
        """
        Turn off the client program,
        send the message of quit to other clients.
        """
        address = self.client.getsockname()
        message = 'Client {}:{} is quit.'.format(address[0], address[1])
        self.client.send(message.encode())
        self.event.set()

    def terminate(self):
        """
        Keep the thread working.
        """
        self.event.wait()

def main():
    c = GroupChatClient_UDP()
    c.start()


if __name__ == '__main__':
    main()
