import base64
import datetime
import json
import pickle
import socket
import sys
import io
import threading
from struct import unpack
from urllib.parse import urlparse

import settings
import time
import textwrap
import email
import pprint
from io import StringIO
import gzip
import logging

# C:\\Users\\Administrator\\PycharmProjects\\geocell_proxy_server\logs\\



class server_manager():
    responces = {}
    https_sesions = {}

    requests_counter = 0
    thread_lock = threading.Lock()

    def clean(self):

        while True:

            dell = []
            for i in self.https_sesions:

                if (datetime.datetime.now() - self.https_sesions[i]['stamp']).total_seconds() > settings.clean_time:
                    try:

                        self.https_sesions[i]['sesion'].close()

                    except:
                        pass

                    try:
                        dell.append(i)
                    except:
                        pass

                    try:
                        del (self.requests[i])
                    except:
                        pass

            for i in dell:
                try:
                    del (self.https_sesions[i])
                except:
                    pass

            time.sleep(7)

    def get_next_request_count(self, *args):

        self.thread_lock.acquire()
        res = self.requests_counter + 1
        self.requests_counter = res
        self.thread_lock.release()
        return res


    def port_range_mapper(self,range_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.bind((settings.remote_server_ip,range_port))
        while True:
            try:

                data, addr = sock.recvfrom(65507)

                thr = threading.Thread(target=self.handle, args=(data, addr, sock))
                thr.daemon = True
                thr.start()
            except:
                pass

    def start_server(self):

        print('[*] start proxy server at ip {} and port {}'.format(settings.remote_server_ip,'-ranged port-'))
        print('[*] protocol http/https')
        print('[*] socket protocol udp')
        print('[*] time:' + str(datetime.datetime.now()))

        # thr2 = threading.Thread(target=self.clean)
        #
        # thr2.start()

        for i in settings.remote_server_port_range:
            thr2 = threading.Thread(target=self.port_range_mapper,args=(i,))

            thr2.start()













    def handle(self, data, addr, conn):
        try:
            datastring=data

            if(datastring.startswith(b'request_id')):

                new_req_id=str(self.get_next_request_count()).encode()
                host=datastring.split(b'|')[1]
                port=int(datastring.split(b'|')[2])






                self.https_sesions[new_req_id]={'stamp':datetime.datetime.now(),'host':host,'port':port,'sesion':None}
                self.responces[new_req_id]=[]
                conn.sendto(new_req_id,addr)


            else:
                try:

                    print(str(data))
                    req_id=data.split(b'|-1327-|')[0]
                    data=data.split(b'|-1327-|')[1]
                    sesion=None
                    if self.https_sesions[req_id]['sesion']:
                        sesion = self.https_sesions[req_id]['sesion']



                    if data:
                        if sesion:
                            print('receive data from client')
                            sesion.sendall(data)



                        else:
                            sesion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sesion.connect((self.https_sesions[req_id]['host'], self.https_sesions[req_id]['port']))

                            self.https_sesions[req_id]['sesion'] = sesion
                            print('receive data from client')
                            sesion.sendall(data)



                    elif sesion:


                         resp=sesion.recv(65000)
                         if resp:
                            print('send data to client')
                            conn.sendto(resp,addr)

                except Exception as e:
                  print(e)
                  logging.exception('msg')

        except Exception as e:
            print(e)










def server():
    a = server_manager()

    a.start_server()


if __name__ == "__main__":
    server()



