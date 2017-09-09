import base64
import datetime
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
import logging

# C:\\Users\\Administrator\\PycharmProjects\\geocell_proxy_server\logs\\
logging.basicConfig(filename='server.log', format='%(asctime)s %(message)s', level=logging.DEBUG)


class server_manager():
    requests = {}
    https_sesions = {}
    
    requests_counter = 0
    thread_lock = threading.Lock()
    
    
    def clean(self):
        while True:
            for i in self.https_sesions:
                if (datetime.datetime.now()-self.https_sesions[i]['stamp']).total_seconds()>settings.clean_time:
                    try:
                       
                         self.https_sesions[i]['sesion'].close()
                    except:pass
                    
                    try:
                         del ( self.https_sesions[i])
                    except:pass
                    
                    try:
                        del(self.requests[i])
                    except:pass
    
    def get_next_request_count(self, *args):
        
        self.thread_lock.acquire()
        res = self.requests_counter + 1
        self.requests_counter = res
        self.thread_lock.release()
        return res
    
    
    def start_server(self):
        
        print('[*] start proxy server at ip {} and port {}'.format(settings.remote_server_ip,
                                                                   str(settings.remote_server_port)))
        print('[*] protocol http/https')
        print('[*] socket protocol udp')
        print('[*] time:' + str(datetime.datetime.now()))
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        sock.bind((settings.remote_server_ip, settings.remote_server_port))

        clth = threading.Thread(target=self.clean)
        clth.start()
        
        while True:
            try:
                
                data, addr = sock.recvfrom(65507)
                
                thr = threading.Thread(target=self.handle, args=(data, addr, sock))
                thr.start()
            except:
                pass
                
                
                
                
                
                
                
                # ბინარი სტრინგი მოდის თავიდან და არა რექვესთი
    
    def get_responce(self, requset, sesion=None, https=False, request_id=None):
        
        data = b''
        sock = ''
        try:
            if not https:
                
                try:
                    _, headers = requset.split('\r\n', 1)
                except Exception as e:
                    logging.exception('message')
                    return

                    # print('sgsg erori')
                    # print(requset)
                    # print(sesion)
                
                # construct a message from the request string
                message = email.message_from_file(StringIO(headers))
                
                # construct a dictionary containing the headers
                headers = dict(message.items())
                headers['method'], headers['path'], headers['http-version'] = _.split()
                
                url = urlparse(headers['path'])
                
                requset = requset.replace(headers['path'], headers['path'].replace(url.scheme + '://' + url.netloc, ''))
                host = headers['Host']
                lr = host.split(':')
                host = lr[0]
                if len(lr) == 2:
                    port = int(lr[1])
                
                else:
                    port = 80
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # Connect the socket to the port where the server is listening
                server_address = (host, port)
                # print(server_address)
                try:
                    sock.connect(server_address)
                except Exception as e:
                    logging.exception('message')
                    return
                sock.sendall(requset.encode())
                
                timeout = settings.global_timeout
                while True:
                    temp = None
                    try:
                        
                        sock.settimeout(timeout)
                        st = datetime.datetime.now()
                        temp = sock.recv(2000)
                        end = datetime.datetime.now()
                        sock.settimeout(None)
                        timeout = (end - st).total_seconds() + 0.1
                    except:
                        sock.settimeout(None)
                        sock.close()
                        
                        break
                    
                    if temp:
                        data += temp
                    else:
                        sock.close()
                        break
            
            
            
            
            else:
                
                if not sesion:
                    sock = ''
                    try:
                        _, headers = requset.split('\r\n', 1)

                        # print('sgsg erori')
                        
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
                        
                        server_address = (host, port)
                        sock.settimeout(settings.global_timeout)
                        sock.connect(server_address)
                        sock.settimeout(None)
                    except Exception as e:
                        sock.close()
                        logging.exception('message')
                        return ''
                    
                    return sock
                else:
                    # print('ses'+str(sesion))
                    sock = sesion
                    
                    requset = base64.decodebytes(requset.encode())
                    try:
                        sock.settimeout(settings.global_timeout)
                        sock.sendall(requset)
                        sock.settimeout(None)
                    except:
                        sock.close()
                        
                        return None
                    timeout = settings.global_timeout
                    while True:
                        try:
                            
                            sock.settimeout(timeout)
                            st = datetime.datetime.now()
                            t_data = sock.recv(65000)
                            end = datetime.datetime.now()
                            sock.settimeout(None)
                            timeout = (end - st).total_seconds() + 0.1
                            if t_data:
                                data += t_data
                            else:
                                sock.close()
                                del (self.https_sesions[request_id])
                        
                        
                        
                        except socket.timeout:
                            
                            sock.settimeout(None)
                            break
                        except:
                            if sock:
                                try:
                                    sock.settimeout(None)
                                    sock.close()
                                except Exception as e:
                                    
                                    sock.close()
                                    logging.exception("message")
                                    logging.info('tipi' + str(sock) + ' :' + str(type(sock)))
                                    print('tipi' + str(sock) + ' :' + str(type(sock)))
                            
                            break
                    # data = gzip.compress(data, compresslevel=6)
                    info = [data[i:i + settings.max_fragment_size] for i in
                            range(0, len(data), settings.max_fragment_size)]
                    return info
            
            # data = gzip.compress(data, compresslevel=6)
            info = [data[i:i + settings.max_fragment_size] for i in range(0, len(data), settings.max_fragment_size)]
            return info
        except:
            return b''
    
    def handle(self, data, addr, conn):
        
        data = data.decode()
        json_data = json.loads(data)
        
        # print(json_data)
        
        
        responce_fragments = []
        
        # ეს ბრძანება მოდის როცა კლიენტი გვიგზავნის ვებ რექუესთის ფრაგმენტს
        # ჩვენ ვუგზავნით 'ack'-ს რომ დავადასტუროთ მიღება
        
        if json_data['op'] == 'send_req_data':
            
            if 'request_id' not in json_data.keys():
                request_id = str(self.get_next_request_count())
            else:
                request_id = json_data['request_id']
            print("received request with id: " + str(request_id))
            # logging.info("received request with id: "+str(request_id))
            resp = json.dumps({'request_id': request_id}, ensure_ascii=False).encode()
            
            conn.sendto(resp, addr)
            
            # veb რექუესთების ლისტში,id-ის მიხედვით ვაგდებ ამ რექვესთს
            
            
            
            self.requests[request_id] = {'request': json_data['data']}
            self.requests[request_id]['responce'] = []


        # ეს ბრძანება მოდის როცა კლიენტი გვეკითხება თუ ვებ respon-სის რამდენი ფრაგმენტს ელოდოს ჩვენგან
        # თუ ამ ბრძანებას მივიღებთ,ეს ნიშნავს რომ კლიენტმა უკვე სრულად გამოგვიგზავნა ვებ request-ი და ეხლა web რესპონსს ელოდება
        # ამავე კოდში უნდა მოხდეს ვებ რექუესთის რეალურ სერვერზე გაგზავნა და ვებ რესპონსის მიღება
        # ვებ რესპონსის მიღების შემდეგ ცვენ ის უნდა დავყოთ ფრაგმენტებად 4000 ბაიტის ზომის და ვებ რექუესტების ლისტში უნდა შევყაროთ
        
        elif json_data['op'] == 'receive_fr_count':
            
            # თუ უკვე რესპონსი გვაქვს ამ რექვესთის,მეორედ რომ აღარ ამოვიღოთ
            if len(self.requests[json_data['request_id']]['responce']) <= 0:
                
                request = self.requests[json_data['request_id']]['request']
                
                del (self.requests[json_data['request_id']]['request'])
                self.requests[json_data['request_id']]['responce'] = []
                res = self.get_responce(request)
                if res:
                    self.requests[json_data['request_id']]['responce'] += res
                else:
                    conn.sendto(str('0').encode(), addr)
                    return
            
            print("received url content with id: " + str(json_data['request_id']))
            # logging.info("received url content with id: " + str(json_data['request_id']))
            
            fragment_list = self.requests[json_data['request_id']]['responce']
            print("received url content with id: " + str(json_data['request_id']) + ' fragment_count:' + str(
                len(fragment_list)))
            # logging.info("received url content with id: " + str(json_data['request_id'])+ ' fragment_count:' +str(len(fragment_list)))
            # print('receive_fragment_count:' +str(len(fragment_list)))
            
            conn.sendto(str(len(fragment_list)).encode(), addr)


        # თუ ეს ბრძანება მივიღეთ ესეიგი კლიენტი ითხოვს ვებ რესპონსის კონკრეტულ ფრაგმენტს ჩვენგან
        elif json_data['op'] == 'receive_fr_data':
            
            if 'action' in json_data.keys():
                
                # დასაფიქსია
                try:
                    self.requests[json_data['request_id']]['responce'][json_data['fr_index']] = ''
                except:
                    logging.error('imena is erori----------------' + str(json_data))
                    return
            
            
            else:
                
                print("fragment request with id: " + str(json_data['request_id']) + ' and fragment id: ' + str(
                    json_data['fr_index']))
                # logging.info("fragment request with id: " + str(json_data['request_id'])+' and fragment id: '+str(json_data['fr_index']))
                
                
                
                resp_fr_data = ''
                try:
                    resp_fr_data = self.requests[json_data['request_id']]['responce'][json_data['fr_index']]
                    
                    conn.sendto(resp_fr_data, addr)
                
                except Exception as e:
                    logging.exception('message')
                    conn.sendto(b'', addr)
                    print('+++++++is erori ' + str(json_data))
                print("gaigzavna: " + str(json_data['request_id']) + ' and fragment id: ' + str(
                    json_data['fr_index']) + ' zoma: ' + str(len(resp_fr_data)))
                # logging.info("gaigzavna: " + str(json_data['request_id']) + ' and fragment id: ' + str(json_data['fr_index']))
        
        
        elif json_data['op'] == 'https_receive_fr_count':
            
            try:
                try:
                    request = self.requests[json_data['request_id']]['request']
                    if request == 'already_received':
                        
                        conn.sendto(str(len(self.requests[json_data['request_id']]['responce'])).encode(), addr)
                        return
                    else:
                        self.requests[json_data['request_id']]['request'] = 'already_received'
                        
                except Exception as e:
                    conn.sendto('0'.encode(), addr)
                    print('((((((((((((((((((=erori da rame ' + str(json_data))
                    logging.exception('message')
                
                
                if json_data['request_id'] in self.https_sesions.keys():
                    sesion = self.https_sesions[json_data['request_id']]['sesion']
                    self.requests[json_data['request_id']]['responce'] = []
                    res = self.get_responce(request, sesion=sesion, https=True, request_id=json_data['request_id'])
                    if res:
                        self.requests[json_data['request_id']]['responce'] += res
                        fragment_list = self.requests[json_data['request_id']]['responce']
                        # print('receive_fragment_count:' + str(len(fragment_list)))
                        conn.sendto(str(len(fragment_list)).encode(), addr)
                    else:
                        conn.sendto('0'.encode(), addr)
                        sesion.close()
                        return
                
                
                
                else:
                    sesion = self.get_responce(request, sesion=None, https=True)
                    if sesion:
                        
                        self.https_sesions[json_data['request_id']] ={'sesion': sesion,'stamp':datetime.datetime.now()}
                    else:
                        conn.sendto('0'.encode(), addr)
                        
                        
                        return
            except:
                conn.sendto('0'.encode(), addr)
                return
        
        
        
        elif json_data['op'] == 'clean':
            if json_data['request_id'] in self.requests:
                del (self.requests[json_data['request_id']])
            if json_data['request_id'] in self.https_sesions:
                self.https_sesions[json_data['request_id']]['sesion'].close()
                


def server():
    a = server_manager()
    
    a.start_server()


if __name__ == "__main__":
    server()



