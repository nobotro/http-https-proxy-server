import base64
import json
import pickle
import socket
import sys
import io
import threading
from urllib.parse import urlparse

import settings
import time
import textwrap
import email
import pprint
from io import StringIO
import gzip
class server_manager():


    requests={}
    https_sesions ={}

    requests_counter = 0
    thread_lock = threading.Lock()

    def get_next_request_count(self, *args):

        self.thread_lock.acquire()
        res = self.requests_counter + 1
        self.requests_counter = res
        self.thread_lock.release()
        return res

    def start_server(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.bind((settings.remote_server_ip, settings.remote_server_port))
        print('[*] start proxy server at ip {} and port {}'.format(settings.remote_server_ip,str(settings.remote_server_port)))
        print('[*] protocol http/https')
        print('[*] socket protocol udp')




        while True:
            try:
                data, addr = sock.recvfrom(65507)

                thr = threading.Thread(target= self.handle, args=(data,addr,sock))
                thr.start()
            except:
             pass







#ბინარი სტრინგი მოდის თავიდან და არა რექვესთი

    def get_responce(self,requset,sesion=None,https=False):

        data = b''
        sock=''

        if not https:

            try:
                _, headers =requset.split('\r\n', 1)
            except:
                pass
               #print('sgsg erori')
                #print(requset)
                #print(sesion)

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
                #print(server_address)
                try:
                 sock.connect(server_address)
                except:

                    pass

                sock.sendall(requset.encode())


                while True:
                    temp=None
                    try:
                        sock.settimeout(settings.global_timeout)
                        temp = sock.recv(67500)
                        sock.settimeout(None)
                    except:
                        sock.settimeout(None)
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
                    pass
                    #print('sgsg erori')

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
                #print('ses'+str(sesion))
                sock =sesion
                requset=base64.decodebytes(requset.encode())




                sock.sendall(requset)

                while True:
                    try:

                        sock.settimeout(settings.global_timeout)
                        t_data = sock.recv(65000)
                        sock.settimeout(None)
                        if t_data:
                            data += t_data
                        else:
                            sock.close()



                    except socket.timeout:
                        sock.settimeout(None)
                        break
                    except:
                        sock.settimeout(None)
                        sock.close()
                        break
                data=gzip.compress(data,compresslevel=6)
                info = [data[i:i + 65507] for i in range(0, len(data), 65507)]
                return info

        data = gzip.compress(data, compresslevel=6)
        info = [data[i:i + 65507] for i in range(0, len(data), 65507)]
        return info







    def handle(self,data,addr,conn):



            data=data.decode()
            json_data=json.loads(data)

            # print(json_data)


            responce_fragments=[]


            #ეს ბრძანება მოდის როცა კლიენტი გვიგზავნის ვებ რექუესთის ფრაგმენტს
            #ჩვენ ვუგზავნით 'ack'-ს რომ დავადასტუროთ მიღება

            if json_data['op']=='send_req_data':

                if 'request_id' not in json_data.keys():
                     request_id=str(self.get_next_request_count())
                else:
                    request_id=json_data['request_id']
                print("received request with id: "+str(request_id))
                resp=json.dumps({'request_id':request_id}, ensure_ascii=False).encode()

                conn.sendto(resp,addr)


                #veb რექუესთების ლისტში,id-ის მიხედვით ვაგდებ ამ რექვესთს



                self.requests[request_id]={'request':json_data['data']}
                self.requests[request_id]['responce']=[]


            #ეს ბრძანება მოდის როცა კლიენტი გვეკითხება თუ ვებ respon-სის რამდენი ფრაგმენტს ელოდოს ჩვენგან
            #თუ ამ ბრძანებას მივიღებთ,ეს ნიშნავს რომ კლიენტმა უკვე სრულად გამოგვიგზავნა ვებ request-ი და ეხლა web რესპონსს ელოდება
            #ამავე კოდში უნდა მოხდეს ვებ რექუესთის რეალურ სერვერზე გაგზავნა და ვებ რესპონსის მიღება
            #ვებ რესპონსის მიღების შემდეგ ცვენ ის უნდა დავყოთ ფრაგმენტებად 4000 ბაიტის ზომის და ვებ რექუესტების ლისტში უნდა შევყაროთ

            elif json_data['op']=='receive_fr_count':

                #თუ უკვე რესპონსი გვაქვს ამ რექვესთის,მეორედ რომ აღარ ამოვიღოთ
                if len(self.requests[json_data['request_id']]['responce'])<=0:

                    request = self.requests[json_data['request_id']]['request']

                    del(self.requests[json_data['request_id']]['request'])
                    self.requests[json_data['request_id']]['responce']=[]
                    self.requests[json_data['request_id']]['responce'] += self.get_responce(request)

                print("received url content with id: " + str(json_data['request_id']))

                fragment_list=self.requests[json_data['request_id']]['responce']
                print("received url content with id: " + str(json_data['request_id'])+ ' fragment_count:' +str(len(fragment_list)))
                # print('receive_fragment_count:' +str(len(fragment_list)))

                conn.sendto(str(len(fragment_list)).encode(),addr)


            #თუ ეს ბრძანება მივიღეთ ესეიგი კლიენტი ითხოვს ვებ რესპონსის კონკრეტულ ფრაგმენტს ჩვენგან
            elif json_data['op']=='receive_fr_data':


                if 'action' in json_data.keys():
                    pass
                    #დასაფიქსია
                    self.requests[json_data['request_id']]['responce'][json_data['fr_index']]=''

                else:

                    print("fragment request with id: " + str(json_data['request_id'])+' and fragment id: '+str(json_data['fr_index']))
                    resp_fr_data=self.requests[json_data['request_id']]['responce'][json_data['fr_index']]


                    try:
                        conn.sendto(resp_fr_data,addr)
                    except:
                        print('+++++++is erori '+str(json_data))
                    print("gaigzavna: " + str(json_data['request_id']) + ' and fragment id: ' + str(
                        json_data['fr_index']))


            elif  json_data['op']=='https_receive_fr_count':
                try:
                    request =self.requests[json_data['request_id']]['request']
                except:

                    print('((((((((((((((((((=erori da rame '+str(json_data))
                    print(self.requests)

                if json_data['request_id'] in self.https_sesions.keys():
                    sesion = self.https_sesions[json_data['request_id']]
                    self.requests[json_data['request_id']]['responce']=[]
                    self.requests[json_data['request_id']]['responce'] += self.get_responce(request, sesion=sesion,https=True)



                else:
                    sesion = self.get_responce(request, sesion=None,https=True)
                    self.https_sesions[json_data['request_id']] = sesion

                fragment_list = self.requests[json_data['request_id']]['responce']
                # print('receive_fragment_count:' + str(len(fragment_list)))
                conn.sendto(str(len(fragment_list)).encode(), addr)




def server():
    a=server_manager()
    a.start_server()
if __name__ == "__main__":
    server()



