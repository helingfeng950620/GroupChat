import socket
import threading
import logging


class GroupChatServer:
    def __init__(self, ip: str, port: int):
        self.address = ip, port
        self.group = {}
        self.event = threading.Event()
        self.log = self.getlogger()
        self.lock_group = threading.Lock()

    @staticmethod
    def getlogger():
        """Create a logger object for each GroupChatServer object
        but it looks useless in my project.
        I just want to practise using logging module."""
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        log = logging.getLogger(__name__)
        log.addHandler(handler)
        log.setLevel(logging.INFO)
        logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S')
        log.propagate = False
        return log

    def start(self):
        """Create anther thread, which is use to accept connection from client.
        The main thread will not block."""
        threading.Thread(target=self.terminate, name='terminate').start()
        threading.Thread(target=self.accept, name='accept', daemon=True).start()

    def accept(self):
        """Use to accept connections of clients
        until GroupChatServer object calls terminate function."""
        with socket.socket() as s:
            s.bind(self.address)
            s.listen()
            while True:  # 不停地循环, 反正有accept阻塞
                client, c_address = s.accept()
                self.lock_group.acquire()
                self.group[c_address] = client  # 这个key是一个二元tuple
                self.lock_group.release()

                self.log.info('Client {}:{} join the group chat.'.format(c_address[0], c_address[1]))
                threading.Thread(target=self.receive,
                                 args=(client, c_address),
                                 name='{}:{}'.format(c_address[0], c_address[1]),
                                 daemon=True).start()

    def receive(self, client: socket.socket, caddr: tuple):
        """Create a thread is ready to receive client's message.
        each client has his own receive thread (start in accept function)."""
        with client:
            while True:
                try:
                    data = client.recv(1024)  # 在这阻塞, 等待接收client的消息
                    if data == b'quit':  # or data == b'':  # 这里修改一下, 感觉是软件的问题, 主动断连接一直发送b"
                        self.quit(caddr)
                        break
                    message = '{}: {}'.format(caddr[1], data.decode(encoding='utf8'))
                    print('{}'.format(message))  # 测试用的, 服务端不需要显示信息
                    for a, c in self.group.items():
                        if a == caddr:
                            continue
                        c.send(message.encode(encoding='utf8'))
                except Exception:
                    self.quit(caddr)
                    break

    def quit(self, caddr):
        message = 'Client {}:{} is quit.'.format(caddr[0], caddr[1])
        self.log.info(message)

        self.lock_group.acquire()
        self.group.pop(caddr)
        self.lock_group.release()

        if len(self.group) == 0:
            self.event.set()
        else:
            for a, c in self.group.items():
                if a == caddr:
                    continue
                c.send(message.encode(encoding='utf8'))

    def terminate(self):
        """Terminate this group chat program when members is ."""
        self.event.wait()
        self.log.info('Group chat is finish.')


def main():
    s = GroupChatServer('127.0.0.1', 9999)
    s.start()


if __name__ == '__main__':
    main()
