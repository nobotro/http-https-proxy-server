import base64
import datetime
import json
import pickle
import socket
import sys
import io
import threading
from urllib.parse import urlparse

import zlib

import settings
import time
import textwrap
import email
import pprint
from io import StringIO
class server_manager():


    requests={}
    https_sesions={}

    def start_server(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('37.187.55.53', 1327))
        sock.listen(5)


        while True:

            conn,addr=sock.accept()
            thr = threading.Thread(target=self.handle, args=(conn, addr))
            thr.start()




#ბინარი სტრინგი მოდის თავიდან და არა რექვესთი

    def get_responce(self,requset,sesion=None,https=False):

        data = b''
        sock=''

        if not https:

            try:
                _, headers =requset.split('\r\n', 1)
            except:
                print('sgsg erori')


            # construct a message from the request string
            message = email.message_from_file(StringIO(headers))

            # construct a dictionary containing the headers
            headers = dict(message.items())
            headers['method'], headers['path'], headers['http-version'] = _.split()

            if headers['method']!='CONNECT':

                url= urlparse(headers['path'])

                requset=requset.replace(headers['path'],headers['path'].replace(url.scheme+'://'+url.netloc,''))
                host=headers['Host']
                lr=host.split(':')
                host=lr[0]
                if len(lr)==2:
                    port=int(lr[1])

                else:port=80








                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connect the socket to the port where the server is listening
                server_address = (host,port)
                # print(server_address)
                try:
                 sock.connect(server_address)
                except:
                    print('shsh')
                sock.sendall(requset.encode())
                print('request----------------------'+requset)

                print('-------------------------------')

                while True:
                    temp=None
                    try:
                        sock.settimeout(3)
                        temp = sock.recv(4096)
                        sock.settimeout(None)
                    except:
                        sock.close()

                        break


                    if temp:
                        data+=temp
                    else:
                        sock.close()
                        break










        else:


            if not sesion:
                sock =''
                try:
                    _, headers = requset.split('\r\n', 1)
                except:
                    print('sgsg erori')

                    # construct a message from the request string
                message = email.message_from_file(StringIO(headers))

                # construct a dictionary containing the headers
                headers = dict(message.items())
                headers['method'], headers['path'], headers['http-version'] = _.split()


                host = headers['path']
                lr = host.split(':')
                host = lr[0]
                if len(lr) == 2:
                    port = int(lr[1])

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connect the socket to the port where the server is listening
                server_address = (host, port)
                sock.connect(server_address)


                return sock
            else:

                sock =sesion
                requset=base64.decodebytes(requset.encode())
                requset=zlib.decompress(requset)




                sock.sendall(requset)
                st = datetime.datetime.now()


                while True:
                    try:
                        sock.settimeout(1)
                        t_data = sock.recv(10000)
                        sock.settimeout(None)
                        if t_data:
                            data += t_data
                        else:

                            sock.close()



                    except socket.timeout:
                        break
                    except:
                        sock.close()
                        break
                end = datetime.datetime.now()

                print('time to get responce' + str(end - st) + 'len' + str(len(data)))
                info = [data[i:i + 8000] for i in range(0, len(data), 8000)]
                return info











        info = [data[i:i + 8000] for i in range(0, len(data), 8000)]
        return info







    def handle(self,conn,addr):

        conn.settimeout(settings.socket_timeout)
        data=conn.recv(4000).decode()
        json_data=json.loads(data)
        # print(json_data)

        conn.settimeout(None)
        responce_fragments=[]


        #ეს ბრძანება მოდის როცა კლიენტი გვიგზავნის ვებ რექუესთის ფრაგმენტს
        #ჩვენ ვუგზავნით 'ack'-ს რომ დავადასტუროთ მიღება

        if json_data['op']=='send_req_data':

            conn.settimeout(settings.socket_timeout)
            conn.sendall('ack'.encode())
            conn.settimeout(None)

            #veb რექუესთების ლისტში,id-ის მიხედვით ვაგდებ ამ რექვესთს



            self.requests[json_data['request_id']]={'request':json_data['data']}
            self.requests[json_data['request_id']]['responce']=[]
            conn.close()

        #ეს ბრძანება მოდის როცა კლიენტი გვეკითხება თუ ვებ respon-სის რამდენი ფრაგმენტს ელოდოს ჩვენგან
        #თუ ამ ბრძანებას მივიღებთ,ეს ნიშნავს რომ კლიენტმა უკვე სრულად გამოგვიგზავნა ვებ request-ი და ეხლა web რესპონსს ელოდება
        #ამავე კოდში უნდა მოხდეს ვებ რექუესთის რეალურ სერვერზე გაგზავნა და ვებ რესპონსის მიღება
        #ვებ რესპონსის მიღების შემდეგ ცვენ ის უნდა დავყოთ ფრაგმენტებად 4000 ბაიტის ზომის და ვებ რექუესტების ლისტში უნდა შევყაროთ

        elif json_data['op']=='receive_fr_count':
            request = self.requests[json_data['request_id']]['request']

            self.requests[json_data['request_id']]['responce'] += self.get_responce(request)

            fragment_list=self.requests[json_data['request_id']]['responce']
            # print('receive_fragment_count:' +str(len(fragment_list)))
            conn.settimeout(settings.socket_timeout)
            conn.sendall(str(len(fragment_list)).encode())
            conn.settimeout(None)
            conn.close()








        #თუ ეს ბრძანება მივიღეთ ესეიგი კლიენტი ითხოვს ვებ რესპონსის კონკრეტულ ფრაგმენტს ჩვენგან
        elif json_data['op']=='receive_fr_data':



            resp_fr_data=self.requests[json_data['request_id']]['responce'][json_data['fr_index']]


            conn.settimeout(settings.socket_timeout)
            conn.sendall(resp_fr_data)
            conn.settimeout(None)
            conn.close()

        elif  json_data['op']=='https_receive_fr_count':

            request =self.requests[json_data['request_id']]['request']

            if json_data['request_id'] in self.https_sesions.keys():
                sesion = self.https_sesions[json_data['request_id']]


                self.requests[json_data['request_id']]['responce'] += self.get_responce(request, sesion=sesion,https=True)



            else:
                sesion = self.get_responce(request, sesion=None,https=True)
                self.https_sesions[json_data['request_id']] = sesion

            fragment_list = self.requests[json_data['request_id']]['responce']
            print('receive_fragment_count:' + str(len(fragment_list)))
            conn.settimeout(settings.socket_timeout)
            conn.sendall(str(len(fragment_list)).encode())
            conn.settimeout(None)
            conn.close()


def server():
    a=server_manager()
    a.start_server()
if __name__ == "__main__":
    server()



