import json
import socket
import sys
import io
import threading

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


        json_data=json.loads(conn.recv(4000).decode(),encoding='utf-8')



        if json_data['op']=='send':

            conn.sendall('ack')


            if self.requests[json_data['request_id']]:
                self.requests[json_data['request_id']].append(json_data['data'])
            else:
                self.requests[json_data['request_id']]=[json_data['data']]










