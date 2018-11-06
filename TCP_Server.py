import selectors
import socket
import threading
import logging


class GroupChatServer:
    def __init__(self, ip, port):
        self.address = ip, port
        self.server_socket = socket.socket()
        self.selector = selectors.DefaultSelector()
        self.group = {}
        self.event = threading.Event()
        self.log = self.getlogger()
        self.setup()

    def start(self):
        """
        Create anther thread,
        which is use to supervise the network IO.
        """
        threading.Thread(target=self.select, name='select').start()

    @staticmethod
    def getlogger():
        """
        Create a logger object for each GroupChatServer object
        but it looks useless in my project.
        I just want to practise using logging module.
        """
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

    def setup(self):
        """
        Do some pre-work.
        """
        self.server_socket.bind(self.address)
        self.server_socket.listen(32)  # .listen函数的backlog, 指定半连接的最大数量, 一般不超过30
        self.server_socket.setblocking(False)
        socket_key = self.selector.register(self.server_socket, selectors.EVENT_READ, data=self.accept)
        self.fd = socket_key.fd

    def accept(self):
        """
        Use to accept connections of clients
        and register the new socket to selector.
        """
        client, address = self.server_socket.accept()
        self.group[address] = client
        client.setblocking(False)  # "推荐改成非阻塞模式", 但是为什么???
        self.log.info('Client {}:{} join the group chat.'.format(address[0], address[1]))
        self.selector.register(client, selectors.EVENT_READ, data=self.handle)

    def handle(self, sock: selectors.SelectorKey):  # Server端不需要读写分离, 收到信息, 转发出去就好
        """
        Receive client's message.
        and send the message to other group members.
        """
        try:
            data, address = sock.fileobj.recvfrom(1024)
            # 这个socket对象, 是Server端和Client端连接的socket对象, 不是Client端的socket对象,
            # 所以这个socket的local address是Server的address, remote address是Client的address.
            if data == b'quit':
                self.quit(address)
            else:
                print(data)
                for a, c in self.group.items():
                    if a == address:
                        continue
                    c.send(data)
        except:
            self.quit(sock.fileobj.getpeername())

    def select(self):
        """
        Create a thread to supervise network IO.
        """
        while not self.event.is_set():
            events = self.selector.select()  # 这里面有个timeout参数
            for sk, mask in events:
                if sk.fd == self.fd:
                    sk.data()
                else:
                   sk.data(sk)

    def quit(self, address):
        """
        Kick client out who send the message "quit" or terminates connection.
        """
        message = 'Client {}:{} is quit.'.format(address[0], address[1])
        self.log.info(message)
        client = self.group.pop(address)
        self.selector.unregister(client)
        client.close()
        for a, c in self.group.items():
            if a == address:
                continue
            c.send(message.encode(encoding='utf8'))

    def finish(self):
        """
        Stop the server.
        """
        self.event.set()
        self.selector.close()
        for c in self.group.values():
            self.selector.unregister(c)
            c.close()
        self.server_socket.close()
        self.log.info('Group chat is finish.')


def main():
    ip = '127.0.0.1'
    port = 9999
    s = GroupChatServer(ip, port)
    s.start()
    while True:
        cmd = input('Server command : ')
        if cmd == 'Server stop':
            s.finish()

            break
        print(s.group)


if __name__ == '__main__':
    main()
