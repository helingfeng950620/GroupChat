import socket
import threading


class GroupChatClient:
    def __init__(self, ip, port):
        self.address = ip, port
        self.sock = socket.socket()
        self.event = threading.Event()

    def start(self):
        """Connect remote address, be receive to accept and send message"""
        self.sock.connect(self.address)
        threading.Thread(target=self.read, name='read', daemon=True).start()
        threading.Thread(target=self.write, name='write', daemon=True).start()
        threading.Thread(target=self.quit, name='quit').start()

    def read(self):
        """Be ready to receive message, it will block on function socket.recv()."""
        while True:
            data = self.sock.recv(1024)
            print('{}'.format(data.decode()))

    def write(self):
        """Be ready to send message, it will block on function input()."""
        while True:
            message = input('>>>')
            if message == 'quit':
                self.event.set()
                break
            self.sock.send(message.encode())

    def quit(self):
        """Keep main thread alive in order to keep read and write thread alive,
        when it finish, read and write thread are finish too because they are daemon thread."""
        self.event.wait()
        print('U have quitted group chat.')


def main():
    c = GroupChatClient('127.0.0.1', 9999)
    c.start()


if __name__ == '__main__':
    main()
