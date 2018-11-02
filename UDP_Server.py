import socket
import threading
import datetime
import time


class GroupChatServer_UDP:
    def __init__(self, ip, port, interval=10):
        self.address = ip, port
        self.event = threading.Event()
        self.clients = {}
        self.interval = interval

    def start(self):
        """
        This function is use to start a group chat server through UDP protocol,
        create a thread which keep receive status.
        """
        threading.Thread(target=self.receive, name='receive', daemon=True).start()

    def receive(self):
        """
        Receive the message from Client,
        send it to all connected clients except sender,
        kick the client out who have not send heart beat package.
        """
        with socket.socket(type=socket.SOCK_DGRAM) as s:
            s.bind(self.address)
            while True:
                data, client_address = s.recvfrom(1024)  # 每次都会阻塞在这里, 就是不发消息, 就不会剔除心跳不存在的客户端
                kick_list = set()
                now = datetime.datetime.now().timestamp()

                if data == b'':
                    self.clients[client_address] = datetime.datetime.now().timestamp()
                    continue
                elif data == b'quit':
                    self.clients.pop(client_address)
                    continue

                print('{}:{}  :\t{}'.format(client_address[0],
                                            client_address[1],
                                            data.decode()))  # 测试用的, 服务器不用显示, 直接转发就行

                for c, t in self.clients.items():

                    if now - t > self.interval:
                        kick_list.add(c)
                        continue
                    elif c == client_address:
                        continue
                    else:
                        s.sendto(data, c)  # 这里怎么把client_address传过去, Client端用来标识

                for c in kick_list:
                    self.clients.pop(c)

    def quit(self):
        """
        Turn on the event, make the only non-daemon thread finish.
        """
        self.event.set()

    def terminate(self):
        """
        Keep the server on.
        """
        self.event.wait()


def main():
    s = GroupChatServer_UDP('127.0.0.1', 9999)
    s.start()
    cmd = input('>>>')
    if cmd == 'quit':
        s.quit()
        # print(threading.enumerate())


if __name__ == '__main__':
    main()
