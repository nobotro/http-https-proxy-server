import json
import socket
import sys
import io
import threading
import settings
import time


class server_manager():


    requests={}

    def start_server(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('37.187.55.53', 1323))
        sock.listen(5)


        while True:

            conn,addr=sock.accept()
            thr = threading.Thread(target=self.request_handler, args=(conn, addr))
            thr.start()

    def handle(self,conn,addr):

        conn.settimeout(settings.socket_timeout)
        json_data=json.loads(conn.recv(4000).decode(),encoding='utf-8')
        conn.settimeout(None)



        if json_data['op']=='send':

            conn.settimeout(settings.socket_timeout)
            conn.sendall('ack')
            conn.settimeout(None)


            if self.requests[json_data['req_id']]:
                self.requests[json_data['req_id']].append(json_data['data'])
            else:
                self.requests[json_data['req_id']]=[json_data['data']]

        elif json_data['op']=='receive':

            fragment_list=self.requests['req_id']

            for fragment in fragment_list









